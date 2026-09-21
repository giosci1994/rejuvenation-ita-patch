# -*- coding: utf-8 -*-
"""
Lettore/scrittore minimale del formato Ruby Marshal 4.8.

Copre il sottoinsieme usato da Pokemon Rejuvenation (messages.dat / intl.dat):
Hash, Array, String (con ivar di encoding), Symbol, Integer, nil, booleani,
Float, Bignum e oggetti user-defined (_dump/_load) come OrderedHash.
"""


class Sym(str):
    """Simbolo Ruby (:Foo). Sottoclasse di str per comodita' d'uso."""
    __slots__ = ()

    def __repr__(self):
        return ":" + str.__str__(self)


class UserDef:
    """
    Oggetto serializzato tramite _dump (marshal type 'u').

    Se l'oggetto ha variabili d'istanza, Ruby avvolge il tutto in un TYPE_IVAR
    ('I') e le scrive dopo il blob: OrderedHash ci mette @keys. Le conserviamo
    per poter riscrivere il file identico all'originale.
    """
    __slots__ = ("cls", "data", "ivars")

    def __init__(self, cls, data, ivars=None):
        self.cls = cls      # Sym col nome della classe
        self.data = data    # bytes grezzi prodotti da _dump
        self.ivars = ivars or {}

    def __repr__(self):
        return "UserDef(%s, %d bytes, ivars=%d)" % (
            self.cls, len(self.data), len(self.ivars))


class RObject:
    """Oggetto generico (marshal type 'o' o 'U')."""
    __slots__ = ("cls", "ivars")

    def __init__(self, cls, ivars):
        self.cls = cls
        self.ivars = ivars

    def __repr__(self):
        return "RObject(%s, %r)" % (self.cls, self.ivars)


# ---------------------------------------------------------------------------
# Reader
# ---------------------------------------------------------------------------
class MarshalReader:
    def __init__(self, data):
        self.d = data
        self.i = 0
        self.symbols = []
        self.objects = []

    def byte(self):
        b = self.d[self.i]
        self.i += 1
        return b

    def bytes_(self, n):
        b = self.d[self.i:self.i + n]
        self.i += n
        return b

    def long(self):
        """Intero compatto Ruby."""
        c = self.byte()
        if c == 0:
            return 0
        if c > 0x7F:
            c -= 0x100
        if 4 < c < 128:
            return c - 5
        if -129 < c < -4:
            return c + 5
        n = abs(c)
        if n > 4:
            raise ValueError("long non valido: %d" % c)
        if c > 0:
            result = 0
            for j in range(n):
                result |= self.byte() << (8 * j)
        else:
            result = -1
            for j in range(n):
                result &= ~(0xFF << (8 * j))
                result |= self.byte() << (8 * j)
        return result

    def load(self):
        if self.bytes_(2) != b"\x04\x08":
            raise ValueError("header Marshal mancante (atteso 4.8)")
        return self.read()

    def _reserve(self):
        self.objects.append(None)
        return len(self.objects) - 1

    def _set(self, idx, val):
        self.objects[idx] = val
        return val

    def read(self):
        t = self.byte()

        if t == 0x30:                       # 0  -> nil
            return None
        if t == 0x54:                       # T
            return True
        if t == 0x46:                       # F
            return False
        if t == 0x69:                       # i  -> fixnum
            return self.long()

        if t == 0x3A:                       # :  -> symbol
            s = Sym(self.bytes_(self.long()).decode("utf-8", "replace"))
            self.symbols.append(s)
            return s
        if t == 0x3B:                       # ;  -> symlink
            return self.symbols[self.long()]
        if t == 0x40:                       # @  -> object link
            return self.objects[self.long()]

        if t == 0x49:                       # I  -> oggetto con ivar
            start = len(self.objects)
            val = self.read()
            n = self.long()
            enc = None
            extra = {}
            for _ in range(n):
                k = self.read()
                v = self.read()
                if k == "E":
                    enc = "utf-8" if v is True else "us-ascii"
                elif k == "encoding":
                    enc = v.decode() if isinstance(v, bytes) else str(v)
                else:
                    extra[k] = v
            if extra and isinstance(val, (UserDef, RObject)):
                val.ivars = extra
            if isinstance(val, bytes):
                val = val.decode(enc or "utf-8", "replace")
                for j in range(len(self.objects) - 1, start - 1, -1):
                    if isinstance(self.objects[j], bytes):
                        self.objects[j] = val
                        break
            return val

        if t == 0x22:                       # "  -> string
            i = self._reserve()
            return self._set(i, self.bytes_(self.long()))

        if t == 0x5B:                       # [  -> array
            i = self._reserve()
            n = self.long()
            arr = []
            self.objects[i] = arr
            for _ in range(n):
                arr.append(self.read())
            return arr

        if t in (0x7B, 0x7D):               # { } -> hash
            i = self._reserve()
            n = self.long()
            h = {}
            self.objects[i] = h
            for _ in range(n):
                k = self.read()
                h[k] = self.read()
            if t == 0x7D:
                self.read()                 # valore di default, ignorato
            return h

        if t == 0x75:                       # u  -> user-defined (_dump)
            i = self._reserve()
            cls = self.read()
            data = self.bytes_(self.long())
            return self._set(i, UserDef(cls, data))

        if t == 0x55:                       # U  -> usermarshal
            i = self._reserve()
            cls = self.read()
            return self._set(i, RObject(cls, self.read()))

        if t == 0x6F:                       # o  -> object
            i = self._reserve()
            cls = self.read()
            n = self.long()
            iv = {}
            self._set(i, RObject(cls, iv))
            for _ in range(n):
                k = self.read()
                iv[k] = self.read()
            return self.objects[i]

        if t == 0x66:                       # f  -> float
            i = self._reserve()
            s = self.bytes_(self.long()).decode()
            return self._set(i, float(s))

        if t == 0x6C:                       # l  -> bignum
            i = self._reserve()
            sign = self.byte()
            raw = self.bytes_(self.long() * 2)
            val = int.from_bytes(raw, "little")
            if sign == 0x2D:
                val = -val
            return self._set(i, val)

        raise ValueError(
            "tipo Marshal non gestito: %r a offset %d" % (chr(t), self.i - 1)
        )


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------
class MarshalWriter:
    """
    Ruby registra ogni oggetto non immediato in una tabella e riscrive le
    occorrenze successive dello STESSO oggetto come link ('@' + indice).
    Replichiamo il comportamento tramite id() per restare byte-compatibili.
    """

    def __init__(self):
        self.out = bytearray()
        self.symbols = {}
        self.objects = {}     # id(oggetto) -> indice nella tabella
        self.objcount = 0
        self._keep = []       # trattiene i riferimenti: id() resta valido

    def byte(self, b):
        self.out.append(b)

    def _register(self, o):
        self.objects[id(o)] = self.objcount
        self.objcount += 1
        self._keep.append(o)

    def _link(self, o):
        """Scrive un link se l'oggetto e' gia' stato serializzato."""
        idx = self.objects.get(id(o))
        if idx is None:
            return False
        self.byte(0x40)
        self.long(idx)
        return True

    def long(self, n):
        if n == 0:
            self.out.append(0)
        elif 0 < n < 123:
            self.out.append(n + 5)
        elif -124 < n < 0:
            self.out.append((n - 5) & 0xFF)
        else:
            buf = bytearray()
            v = n
            if v > 0:
                while v > 0:
                    buf.append(v & 0xFF)
                    v >>= 8
                self.out.append(len(buf))
            else:
                while v < -1:
                    buf.append(v & 0xFF)
                    v >>= 8
                self.out.append((-len(buf)) & 0xFF)
            self.out.extend(buf)

    def dump(self, obj):
        self.out.extend(b"\x04\x08")
        self.write(obj)
        return bytes(self.out)

    def sym(self, s):
        if s in self.symbols:
            self.byte(0x3B)
            self.long(self.symbols[s])
        else:
            self.symbols[s] = len(self.symbols)
            raw = str(s).encode("utf-8")
            self.byte(0x3A)
            self.long(len(raw))
            self.out.extend(raw)

    def write(self, o):
        if o is None:
            self.byte(0x30)
        elif o is True:
            self.byte(0x54)
        elif o is False:
            self.byte(0x46)
        elif isinstance(o, Sym):
            self.sym(o)
        elif isinstance(o, bool):
            self.byte(0x54 if o else 0x46)
        elif isinstance(o, int):
            if -(2 ** 30) <= o < 2 ** 30:
                self.byte(0x69)
                self.long(o)
            else:
                raise ValueError("bignum in scrittura non supportato: %d" % o)
        elif isinstance(o, float):
            if self._link(o):
                return
            self._register(o)
            raw = repr(o).encode()
            self.byte(0x66)
            self.long(len(raw))
            self.out.extend(raw)
        elif isinstance(o, str):
            # CPython tiene in cache la stringa vuota e quelle di un solo
            # carattere latin-1: sarebbero oggetti distinti in Ruby, quindi
            # non vanno mai collegate. Le altre nascono fresche dal decode.
            if len(o) > 1 and self._link(o):
                return
            raw = o.encode("utf-8")
            self._register(o)
            self.byte(0x49)                 # wrapper ivar per l'encoding
            self.byte(0x22)
            self.long(len(raw))
            self.out.extend(raw)
            self.long(1)
            self.sym(Sym("E"))
            self.byte(0x54)                 # true -> UTF-8
        elif isinstance(o, bytes):
            if self._link(o):
                return
            self._register(o)
            self.byte(0x22)
            self.long(len(o))
            self.out.extend(o)
        elif isinstance(o, list):
            if self._link(o):
                return
            self._register(o)
            self.byte(0x5B)
            self.long(len(o))
            for v in o:
                self.write(v)
        elif isinstance(o, dict):
            if self._link(o):
                return
            self._register(o)
            self.byte(0x7B)
            self.long(len(o))
            for k, v in o.items():
                self.write(k)
                self.write(v)
        elif isinstance(o, UserDef):
            if self._link(o):
                return
            self._register(o)
            if o.ivars:
                self.byte(0x49)             # wrapper per le ivar (es. @keys)
            self.byte(0x75)
            self.sym(o.cls)
            self.long(len(o.data))
            self.out.extend(o.data)
            if o.ivars:
                self.long(len(o.ivars))
                for k, v in o.ivars.items():
                    self.sym(k)
                    self.write(v)
        elif isinstance(o, RObject):
            if self._link(o):
                return
            self._register(o)
            self.byte(0x6F)
            self.sym(o.cls)
            self.long(len(o.ivars))
            for k, v in o.ivars.items():
                self.sym(k)
                self.write(v)
        else:
            raise ValueError("tipo Python non serializzabile: %r" % type(o))


def load(data):
    return MarshalReader(data).load()


def dump(obj):
    return MarshalWriter().dump(obj)


def load_file(path):
    with open(path, "rb") as f:
        return load(f.read())


def dump_file(path, obj):
    with open(path, "wb") as f:
        f.write(dump(obj))
