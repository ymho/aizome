\version "2.22.1"

\header {
  title = "Aizome Étude"
  subtitle = "for a quiet evening"
  composer = "Sample"
  tagline = ##f
}

\paper {
  #(set-paper-size "a5landscape")
  indent = 0\mm
}

global = {
  \key a \minor
  \time 4/4
  \tempo "Andante, semplice" 4 = 76
}

rightHand = \relative c'' {
  \global
  a4\p( c e a) | g2( e) | f4( a c b) | a2.( e4) |
  d4( f a d) | c2( a) | b4( gis e gis) | a2.( e4) |

  c'4\mf( b a e) | f2( e) | d4( e f a) | gis1 |
  a4\>( g f e) | d2( c) | b4( gis e gis) | a1\pp\fermata \bar "|."
}

leftHand = \relative c {
  \global
  <a e'>1 | <e b'> | <f c'> | <e b'> |
  <d a'> | <a e'> | <e b'> | <a e'> |
  <c g'> | <f c'> | <d a'> | <e b'> |
  <f c'> | <d a'> | <e b'> | <a e'> |
}

\score {
  \new PianoStaff <<
    \new Staff = "right" \with { midiInstrument = "acoustic grand" } \rightHand
    \new Staff = "left" \with { midiInstrument = "acoustic grand" } {
      \clef bass
      \leftHand
    }
  >>
  \layout { }
}
