# Ridefinisce le lingue DOPO il secondo caricamento di Rejuv/Settings,
# che altrimenti azzererebbe LANGUAGES. Vedi ScriptLoader.rb riga 165.
# Generato da strumenti/costruisci.py - non modificare a mano.
LANGUAGES = {
  "English"  => nil,
  "Italiano" => "patch/italiano.dat",
}

# --- Accordo di genere ------------------------------------------------------
# L'inglese non distingue il genere di chi parla con te, quindi il gioco ha una
# sola frase per tutte e tre le scelte iniziali. L'italiano invece accorda, e
# "sei pronto" a una giocatrice suona sbagliato.
#
# Questo codice introduce \gg[o|a] : diventa "o" per chi gioca uomo, "a" per
# donna, "*" per non binario. Con tre forme, \gg[o|a|x], la terza vale per il
# non binario.
#
# La scelta sta in $game_variables[:Player_Gender], come documentato in
# Scripts/EncounterModifiers.rb: 0 uomo, 1 donna, 2 non binario.
# NON si usa $Trainer.gender, che in Rejuvenation 14.0 restituisce sempre 2.
module MessageTypes
  GENERE_NON_BINARIO = "*"

  def self.generePersona
    return 0 unless defined?($game_variables) && $game_variables
    begin
      g = $game_variables[:Player_Gender]
      return g.to_i if g.is_a?(Numeric)
    rescue StandardError
    end
    return 0
  end

  def self.espandiGenere(testo)
    return testo unless testo.is_a?(String) && testo.include?('\gg[')
    g = self.generePersona
    testo.gsub(/\\gg\[([^\]\|]*)\|([^\]\|]*)(?:\|([^\]]*))?\]/) do
      maschile, femminile, altro = $1, $2, $3
      case g
      when 1 then femminile
      when 2 then (altro && !altro.empty?) ? altro : GENERE_NON_BINARIO
      else maschile
      end
    end
  end

  class << self
    unless method_defined?(:getFromHash_prima_del_genere)
      alias_method :getFromHash_prima_del_genere, :getFromHash
      alias_method :getFromMapHash_prima_del_genere, :getFromMapHash

      def getFromHash(type, key)
        espandiGenere(getFromHash_prima_del_genere(type, key))
      end

      def getFromMapHash(type, key)
        espandiGenere(getFromMapHash_prima_del_genere(type, key))
      end
    end
  end
end
