// vim: foldmethod=marker

//{{{ function: cycle_styles
function cycle_styles() {
    var ss = document.getElementById("style");
    //window.alert(ss.href);

    var styles = [ "style1.css", "style2.css", "style3.css", "style4.css" ];
    styles.push(styles[0]); // for cyclicity

    for ( var i=0; i<styles.length; i++) 
        {
        if ( ss.href.endsWith(styles[i]) )
            {
            ss.setAttribute('href', ss.href.replace(styles[i], styles[i+1]));
            break;
            }
        }

    }
//}}}

//{{{ collection: chords
//{{{ function: hide_chords
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
//{{{ function: get_notes
function get_notes(which,prefer_sharp=false) {
    notes = [ 'A', 'Bb', 'B', 'C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab' ];
    if ( prefer_sharp || which.match(/#/) ) {
        notes = [ 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#' ];
        }
    return notes.concat(notes);
    }
//}}}
//{{{ function: get_root
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
//{{{ function: get_bass
function get_bass(chord) {
    var array = chord.match( RegExp( "/([a-zb#]+) *$", "i" ) );
    if ( array ) return array[1];
    return null;
    }
//}}}
//{{{ function: increment_note
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
//{{{ function: cycle_chord_div
function cycle_chord_div(d, up) {
    var orig_length = d.innerHTML.length;
    var root = get_root(d.innerHTML);
    var bass = get_bass(d.innerHTML);
    if ( root ) {
        var new_root = increment_note(root, up);
        d.innerHTML = d.innerHTML.replace( RegExp("^" + root), new_root );
        }
    if ( bass ) {
        var new_bass = increment_note(bass, up).toLowerCase();
        d.innerHTML = d.innerHTML.replace( RegExp("/" + bass, "i"), "/" + new_bass );
        }

    // pad to original length
    d.innerHTML = d.innerHTML.replace( RegExp(" *$"), "");
    while ( d.innerHTML.length < orig_length )
        {
        d.innerHTML = d.innerHTML + " ";
        }

    }
//}}}
//{{{ function: transpose_all_chords
function transpose_all_chords(up=true) {
    var divs = document.getElementsByClassName('chord');
    for ( var i=0; i<divs.length; i++) {
        cycle_chord_div(divs[i], up);
        }
    }
//}}}
//}}}
//{{{ collection: capos
//{{{ function: numeral_to_decimal
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
//{{{ function: decimal_to_numeral
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
//{{{ function: get_position
function get_position(d) {
    var array = d.innerHTML.match( RegExp( "(-?[0XIV]+)", "i" ) );
    position_numeral = array[1];
    position_decimal = numeral_to_decimal(position_numeral);
    return position_decimal
    }
//}}}
//{{{ function: cycle_capo_div
function cycle_capo_div(d, up) {
    var new_position = get_position(d);

    if ( up ) { new_position += 1; }
    else      { new_position -= 1; }

    new_position = new_position % 12;
    d.innerHTML = decimal_to_numeral(new_position);
    }
//}}}
//{{{ function: transpose_all_capos
function transpose_all_capos(up=true) {
    var divs = document.getElementsByClassName('capo');
    for ( var i=0; i<divs.length; i++) 
        {
        cycle_capo_div(divs[i], up);
        } 
    }
//}}}
//}}}

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
function cycle_versions(song_index,up) 
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
    if ( up )
        {
        if ( current == versions.length-1 ) { current = 0 }
        else { current += 1 }
        }
    else
        {
        if ( current == 0 ) { current = versions.length-1 }
        else { current -= 1 }
        }

    // show new version and set selector
    versions[current].style.display = "block";
    set_version_selector(song_index, current);
    }
//}}}
//{{{ function: show_all_versions
function show_all_versions()
    {
    var versions = [];
    var divs = document.getElementsByTagName("div");

    for ( var i=0; i<divs.length; i++ )
        {
        if ( divs[i].classList.contains("version") )
            {
            divs[i].style.display = "block";
            }
        }

    return versions;
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
//{{{ function: update_song_version
function update_song_version(song_index)
    {
    var selector = document.getElementById( song_index + ".select")
    var value = selector.options[selector.selectedIndex].value;
    set_version_of_song(song_index, value);
    }
//}}}

//{{{ function: reset_version_selectors
function reset_version_selectors()
    {
    var selectors = document.getElementsByTagName("select");
    for ( var i=0; i<selectors.length; i++ )
        {
        selectors[i].value = 0;
        }
    }
//}}}
//{{{ function: set_version_selector
function set_version_selector(song_id, index)
    {
    var selector = document.getElementById(song_id + ".select");
    selector.value = index;
    }
//}}}

//{{{ function: get_divs_of_song
function get_divs_of_song(song_index, cls)
    {
    var divs = [];
    var all_divs = document.getElementsByTagName("div");

    for ( var i=0; i<all_divs.length; i++ )
        {
        if ( all_divs[i].classList.contains(cls) && 
             (
             // chord is directly in the version div:
             all_divs[i].parentNode.id == song_index
             // chord is in a span div in the version div:
          || all_divs[i].parentNode.parentNode.id == song_index
             )
            )
            {
            divs.push(all_divs[i]);
            }
        }

    return divs;
    }
//}}}
//{{{ function: transpose_song
function transpose_song(song_index, up)
    {
    var chords = get_divs_of_song(song_index, "chord");
    var capos = get_divs_of_song(song_index, "capo");

    for ( var i=0; i<chords.length; i++ )
        {
        cycle_chord_div(chords[i], up);
        }

    for ( var i=0; i<capos.length; i++ )
        {
        cycle_capo_div(capos[i], up);
        }

    }
//}}}
//{{{ function: transpose_all_songs
function transpose_all_songs(up) {
    transpose_all_chords(up);  
    transpose_all_capos(!up);  
    }
//}}}
//{{{ function: topmost_song
function topmost_song()
    {
    var divs = document.getElementsByTagName("div");
    var y_offset = window.pageYOffset; // equal to document.body.scrollTop ?

    for ( var i=0; i<divs.length; i++ )
        {
        if ( divs[i].classList.contains("version") &&
             divs[i].style.display == "block" )
            {
            var rect = divs[i].getBoundingClientRect();

            if ( divs[i].offsetTop >= y_offset )
                {
                return divs[i];
                }
            }
        }

    return;
    }
//}}}
//{{{ function: transpose_topmost_song
function transpose_topmost_song(up)
    {
    var song_div = topmost_song();
    transpose_song(song_div.id, up);
    }
//}}}

//{{{ function: assign_shortcuts
function assign_shortcuts()
    {
    shortcut.add("a",function() { show_all_versions() });
    shortcut.add("j",function() { transpose_topmost_song(false) });
    shortcut.add("k",function() { transpose_topmost_song(true)  });
    }
//}}}

//{{{ function: handle_horizontal_swipe
function handle_horizontal_swipe() 
    {
    var tolerance = 100;
    if ( touchstartX - touchendX > tolerance )
        {
        // alert('swiped left!')
        var song = topmost_song();
        cycle_versions(song.id, true);
        }
    if ( touchendX - touchstartX > tolerance ) 
        {
        // alert('swiped right!')
        var song = topmost_song();
        cycle_versions(song.id, false);
        }
    }
//}}}

let touchstartX = 0
let touchendX = 0

document.addEventListener('touchstart', e => {
    touchstartX = e.changedTouches[0].screenX
    })

document.addEventListener('touchend', e => {
    touchendX = e.changedTouches[0].screenX
    handle_horizontal_swipe()
    })

document.addEventListener('DOMContentLoaded', reset_version_selectors, false);
window.onload = assign_shortcuts;
document.write('<script src="shortcut.js"></script>');

