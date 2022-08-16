// vim: foldmethod=marker

//{{{ function: cycle_styles()
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
//}}}

//{{{ collection: chords
//{{{ function: hide_chords()
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
//}}}
//{{{ function: get_notes()
function get_notes(which,prefer_sharp=false) {
    notes = [ 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab' ];
    if ( prefer_sharp || which.match(/#/) ) {
        notes = [ 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#' ];
        }
    return notes.concat(notes);
    }
//}}}
//{{{ function: get_root()
function get_root(chord) {
    var notes = ["A#","Ab","A","Bb","B","C#","C","D#","Db","D","Eb","E","F#","F","G#","Gb","G","A#"];
    for ( var i=0; i<notes.length; i++ ) {
        if ( chord.match( RegExp( "^" + notes[i] ) ) ) {
            return notes[i];
            }
        }
    return null;
    }
//}}}
//{{{ function: get_bass()
function get_bass(chord) {
    var array = chord.match( RegExp( "/([a-zb#]+)$", "i" ) );
    if ( array ) return array[1];
    return null;
    }
//}}}
//{{{ function: increment_note()
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
//}}}
//{{{ function: chordDivUp()
function chordDivUp(d) {
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
//}}}
//{{{ function: chordDivDown()
function chordDivDown(d) {
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
//}}}
//{{{ function: cycleChords()
function cycleChords(up=true) {
    var divs = document.getElementsByClassName('chord');
    for ( var i=0; i<divs.length; i++) {
        if ( up ) {
            chordDivUp(divs[i]);
            }
        else {
            chordDivDown(divs[i]);
            }
        } 
    }
//}}}
//}}}
//{{{ collection: capos
//{{{ function: numeral_to_decimal()
function numeral_to_decimal(numeral) {
    var mult = 1;
    if ( numeral.startsWith("-") ) {
        mult = -1;
        numeral = numeral.slice(1);
        }
    var numerals = ["0","I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV"];
    var decimal = 0;
    for ( var i=0; i<numerals.length; i++ ) {
        if ( numeral == numerals[i] ) {
            decimal = i;
            break;
            }
        }
    return mult * decimal
    }
//}}}
//{{{ function: decimal_to_numeral()
function decimal_to_numeral(decimal) {
    var mult = "";
    if ( decimal < 0 ) {
        mult = "-";
        decimal *= -1;
        }
    var numerals = ["0","I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV"];
    return mult + numerals[decimal]
    }
//}}}
//{{{ function: get_position()
function get_position(d) {
    var array = d.innerHTML.match( RegExp( "(-?[0XIV]+)", "i" ) );
    position_numeral = array[1];
    position_decimal = numeral_to_decimal(position_numeral);
    return position_decimal
    }
//}}}
//{{{ function: capoDivUp()
function capoDivUp(d) {
    var new_position = get_position(d) + 1;
    new_position = new_position % 12;
    d.innerHTML = decimal_to_numeral(new_position);
    }
//}}}
//{{{ function: capoDivDown()
function capoDivDown(d) {
    var new_position = get_position(d) - 1;
    new_position = new_position % 12;
    d.innerHTML = decimal_to_numeral(new_position);
    }
//}}}
//{{{ function: cycleCapos()
function cycleCapos(up=true) {
    var divs = document.getElementsByClassName('capo');
    for ( var i=0; i<divs.length; i++) {
        if ( up ) {
            capoDivUp(divs[i]);
            }
        else {
            capoDivDown(divs[i]);
            }
        } 
    }
//}}}
//}}}

function transpose_up() {
    cycleChords(true);  
    cycleCapos(false);  
    }

function transpose_down() {
    cycleChords(false); 
    cycleCapos(true);  
    }

//{{{ function: get_versions_of_song
function get_versions_of_song(song_index) 
    {
    var versions = [];
    var divs = document.getElementsByTagName("div");

    for ( var i=0; i<divs.length; i++ )
        {
        if ( divs[i].classList.contains("version") && divs[i].id == song_index )
            {
            versions.push(divs[i]);
            }
        }

    return versions;
    }
//}}}
//{{{ function: cycle_versions
function cycle_versions(song_index,direction) 
    {
    var versions = get_versions_of_song(song_index);
    var current = -1;

    // set current index and hide it:
    for ( var i=0; i<versions.length; i++ )
        {
        if ( versions[i].style.display == "block" ) { current = i; }
        versions[i].style.display = "none"; // "block"
        }

    // set current to next or previous:
    if ( direction > 0 )
        {
        if ( current == versions.length-1 ) { current = 0 }
        else { current += 1 }
        }
    else
        {
        if ( current == 0 ) { current = versions.length-1 }
        else { current -= 1 }
        }

    // show new current:
    versions[current].style.display = "block";
    }
//}}}
//{{{ function: set_version_of_song
function set_version_of_song(song_index,version_index) 
    {
    var versions = get_versions_of_song(song_index);

    for ( var i=0; i<versions.length; i++ )
        {
        if ( i == version_index )
            {
            versions[i].style.display = "block";
            }
        else
            {
            versions[i].style.display = "none";
            }
        }
    }
//}}}

//{{{ function: get_chords_of_song
function get_chords_of_song(song_index)
    {
    var chords = [];
    var divs = document.getElementsByTagName("div");

    for ( var i=0; i<divs.length; i++ )
        {
        if ( divs[i].classList.contains("chord") && 
             divs[i].parentNode.parentNode.id == song_index )
            {
            chords.push(divs[i]);
            }
        }

    return chords;
    }
//}}}
//{{{ function: transpose_song
function transpose_song(song_index, direction)
    {
    var chords = get_chords_of_song(song_index);

    for ( var i=0; i<chords.length; i++ )
        {
        if (direction > 0) { chordDivUp(chords[i]); }
        else               { chordDivDown(chords[i]); }
        }

    }
//}}}

//{{{ function: update_song_version
function update_song_version(song_index)
    {
    var select = document.getElementById( song_index + ".select")
    var value = select.options[select.selectedIndex].value;
    set_version_of_song(song_index, value);
    }
//}}}

//{{{ function: reset_select_boxes
function reset_select_boxes()
    {
    var selects = document.getElementsByTagName("select");
    for ( var i=0; i<selects.length; i++ )
        {
        selects[i].value = 0;
        }
    }
//}}}

document.addEventListener('DOMContentLoaded', reset_select_boxes, false);
shortcut.add("j",function() { transpose_down() });
shortcut.add("k",function() { transpose_up()   });

