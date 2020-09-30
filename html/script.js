
function cycle_styles() {
    var ss = document.getElementById("style");
    //window.alert(ss.href);

    if ( ss.href.endsWith("style1.css") )
        ss.setAttribute('href', ss.href.replace("style1.css", "style2.css"));
    else if ( ss.href.endsWith("style2.css") )
        ss.setAttribute('href', ss.href.replace("style2.css", "style3.css"));
    else if ( ss.href.endsWith("style3.css") )
        ss.setAttribute('href', ss.href.replace("style3.css", "style4.css"));
    else if ( ss.href.endsWith("style4.css") )
        ss.setAttribute('href', ss.href.replace("style4.css", "style1.css"));


    // if ( document.getElementById("style_alt").disabled ) {
    //     document.getElementById("style_alt").disabled  = false;
    //     document.getElementById("style").disabled = true;
    //     }
    // else {
    //     document.getElementById("style_alt").disabled  = true;
    //     document.getElementById("style").disabled = false;
    //     }
    }

function hide_chords() {
    // var songs = document.querySelectorAll('.chords_1col,.chords_2col,.chords_3col');
    // for ( var i=0; i<songs.length; i++) {
    //     songs[i].style.whiteSpace = "normal";
    //     } 
    var chords = document.querySelectorAll('.chord,.tabline,.capo,.tuning,.fingering');

    if ( chords[0].style.display == "none" )
        {
        for ( var i=0; i<chords.length; i++) {
            chords[i].style.display = "inline";
            } 
        }
    else
        {
        for ( var i=0; i<chords.length; i++) {
            chords[i].style.display = "none";
            } 
        } 
    }

function get_notes(which,prefer_sharp=false) {
    notes = [ 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab' ];
    if ( prefer_sharp || which.match(/#/) ) {
        notes = [ 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#' ];
        }
    return notes.concat(notes);
    }

function get_root(chord) {
    var notes = ["A#","Ab","A","Bb","B","C#","C","D#","Db","D","Eb","E","F#","F","G#","Gb","G","A#"];
    for ( var i=0; i<notes.length; i++ ) {
        if ( chord.match( RegExp( "^" + notes[i] ) ) ) {
            return notes[i];
            }
        }
    return null;
    }

function get_bass(chord) {
    var array = chord.match( RegExp( "/([a-zb#]+)$", "i" ) );
    if ( array ) return array[1];
    return null;
    }

function increment_note(note,up=true) {
    var notes = get_notes(note);
    var index = 0;
    
    for ( index = 0; index<notes.length; index++ ) {
        if ( notes[index].toUpperCase() == note.toUpperCase() ) break;
        }
    
    notes = get_notes(note,up); // update chords to account for prefer_sharp

    if ( up ) {
        index += 1;
        if ( index == notes.length ) { index = 0; }
        }
    else {
        index -= 1;
        if ( index == -1 ) { index = notes.length-1; }
        }
    return notes[index];
    }

function divUp(d) {
    var root = get_root(d.innerHTML);
    var bass = get_bass(d.innerHTML);
    if ( root ) {
        var new_root = increment_note(root,true);
        d.innerHTML = d.innerHTML.replace( RegExp("^" + root), new_root );
        }
    if ( bass ) {
        var new_bass = increment_note(bass,true).toLowerCase();
        d.innerHTML = d.innerHTML.replace( RegExp("/" + bass, "i"), "/" + new_bass );
        }

    }

function divDown(d) {
    var root = get_root(d.innerHTML);
    var bass = get_bass(d.innerHTML);
    if ( root ) {
        var new_root = increment_note(root,false);
        d.innerHTML = d.innerHTML.replace( RegExp("^" + root), new_root );
        }
    if ( bass ) {
        var new_bass = increment_note(bass,false).toLowerCase();
        d.innerHTML = d.innerHTML.replace( RegExp("/" + bass, "i"),  "/" + new_bass );
        }
    }

function cycleChords(up=true) {
    var divs = document.getElementsByClassName('chord');
    for ( var i=0; i<divs.length; i++) {
        if ( up ) {
            divUp(divs[i]);
            }
        else {
            divDown(divs[i]);
            }
        } 
    }

function transpose_up()   { cycleChords(true);  }
function transpose_down() { cycleChords(false); }

shortcut.add("j",function() { transpose_down() });
shortcut.add("k",function() { transpose_up() });

