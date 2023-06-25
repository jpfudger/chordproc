// vim: foldmethod=marker

//{{{ function: toggle_multicolumn
function toggle_multicolumn()
    {
    // switch between style (1,2) or (3,4)
    var ss = document.getElementById("style");

    if ( ss.href.endsWith("style1.css") )
        {
        ss.setAttribute('href', ss.href.replace("style1", "style2"));
        set_style_cookie("style2.css")
        }
    else if ( ss.href.endsWith("style2.css") )
        {
        ss.setAttribute('href', ss.href.replace("style2", "style1"));
        set_style_cookie("style1.css")
        }
    else if ( ss.href.endsWith("style3.css") )
        {
        ss.setAttribute('href', ss.href.replace("style3", "style4"));
        set_style_cookie("style4.css")
        }
    else if ( ss.href.endsWith("style4.css") )
        {
        ss.setAttribute('href', ss.href.replace("style4", "style3"));
        set_style_cookie("style3.css")
        }

    }
//}}}
//{{{ function: toggle_dark_mode
function toggle_dark_mode()
    {
    // switch between style (1,3) or (2,4)
    var ss = document.getElementById("style");

    if ( ss.href.endsWith("style1.css") )
        {
        ss.setAttribute('href', ss.href.replace("style1", "style3"));
        set_style_cookie("style3.css")
        }
    else if ( ss.href.endsWith("style3.css") )
        {
        ss.setAttribute('href', ss.href.replace("style3", "style1"));
        set_style_cookie("style1.css")
        }
    else if ( ss.href.endsWith("style2.css") )
        {
        ss.setAttribute('href', ss.href.replace("style2", "style4"));
        set_style_cookie("style4.css")
        }
    else if ( ss.href.endsWith("style4.css") )
        {
        ss.setAttribute('href', ss.href.replace("style4", "style2"));
        set_style_cookie("style2.css")
        }

    }
//}}}

//{{{ function: set_style_cookie
function set_style_cookie(cs) 
    { 
    document.cookie = "Stylesheet=" + cs; 
    }
///}}}
//{{{ function: get_style_cookie
function get_style_cookie(cs) 
    {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; Stylesheet=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    }
//}}}
//{{{ function: del_style_cookie
function del_style_cookie(cs)
    { 
    document.cookie = "Stylesheet=";
    }
//}}}
//{{{ function: cycle_styles
function cycle_styles(prefer=null) {
    var ss = document.getElementById("style");
    //window.alert(ss.href);

    var styles = [ "style1.css", "style2.css", "style3.css", "style4.css" ];
    styles.push(styles[0]); // for cyclicity

    if ( prefer ) { styles = [ "style1.css", prefer ]; }

    for ( var i=0; i<styles.length; i++) 
        {
        if ( ss.href.endsWith(styles[i]) )
            {
            ss.setAttribute('href', ss.href.replace(styles[i], styles[i+1]));
            set_style_cookie(styles[i+1]);
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

    // This function just makes all the version divs visible.
    // It doesn't add a title or a divider, so it can be hard
    // to tell them apart.

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
//{{{ function: cycle_topmost_song
function cycle_topmost_song(up)
    {
    var song_div = topmost_song();
    cycle_versions(song_div.id, up);
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

//{{{ function: goto_dylan
function goto_dylan()
    {
    var url = window.location.pathname;
    url = url.replace(RegExp("\\w+\\.html.*"), "bobdylan.html");
    window.location.href = url;
    return;
    }
//}}}

//{{{ function: get_divs_of_song
function get_divs_of_song(song_index, classes=[])
    {
    var divs = [];
    var all_divs = document.getElementsByTagName("div");
    var keep = false;
    var div = null;

    for ( var i=0; i<all_divs.length; i++ )
        {
        div = all_divs[i];

        keep = false;
        var tmp_div = div
        while ( tmp_div.parentNode != null )
            {
            if ( tmp_div.classList.contains("version") &&
                 tmp_div.style.display == "none" )
                {
                keep = false;
                break;
                }

            if ( tmp_div.id == song_index )
                {
                keep = true;
                break;
                }
            tmp_div = tmp_div.parentNode;
            }
        if ( !keep ) { continue; }

        keep = false;
        for ( var j=0; j<classes.length; j++ )
            {
            if ( div.classList.contains(classes[j]) )
                {
                keep = true;
                break;
                }
            }

        if ( keep ) { divs.push(div); }

        }

    return divs;
    }
//}}}
//{{{ function: transpose_song
function transpose_song(song_index, up)
    {
    var chords = get_divs_of_song(song_index, ["chord"]);
    var capos = get_divs_of_song(song_index, ["capo"]);

    for ( var i=0; i<chords.length; i++ )
        {
        cycle_chord_div(chords[i], up);
        }

    for ( var i=0; i<capos.length; i++ )
        {
        cycle_capo_div(capos[i], !up);
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
    // Note: this function attaches the title (from the preceding h3) as .title
    var elements = document.getElementsByTagName("*");
    var y_offset = window.pageYOffset; // equal to document.body.scrollTop ?

    var current_title = null;

    for ( var i=0; i<elements.length; i++ )
        {
        var elem = elements[i];

        if ( elem.tagName == "H3" )
            {
            current_title = elem.innerHTML;
            }

        if ( elem.tagName == "DIV" && 
             elem.classList.contains("version") &&
             elem.style.display == "block" )
            {
            var rect = elem.getBoundingClientRect();

            if ( elem.offsetTop >= y_offset )
                {
                elem.title = current_title;

                if ( !elem.hasOwnProperty("raw") )
                    {
                    // store default lines for easy restoring
                    elem.raw = elem.innerHTML;
                    }

                return elem;
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

//{{{ function: get_scale
function get_scale(key)
    {
    var scale = [ key ];
    var intervals = [ 2, 2, 1, 2, 2, 2, 1 ];
    var notes = get_notes(key, key.includes("#"));
    var index = notes.indexOf(key);

    for ( var i=0; i<intervals.length; i++ )
        {
        index += intervals[i];
        scale.push(notes[index]);
        }

    // alert(key + " scale: " + scale.join(","))

    return scale;
    }
//}}}
//{{{ function: nashville_chord
function nashville_chord(chord_div, key)
    {
    var root = get_root(chord_div.innerHTML);
    var scale = get_scale(key);
    var degree = scale.indexOf(root) + 1;
    if ( !degree )
        {
        // alert("No " + root + " in " + key);
        }
    var numeral = decimal_to_numeral(degree);
    // alert("key " + key + " : " + root + " = " + degree + " = " + numeral);
    chord_div.innerHTML = chord_div.innerHTML.replace(RegExp("^" + root), numeral);
    }
//}}}
//{{{ function: nashville_system
function nashville_system()
    {
    var song_div = topmost_song();

    if ( song_div.hasOwnProperty("nashville") )
        {
        song_div.innerHTML = song_div.raw;
        delete song_div.nashville;
        return;
        }

    song_div.nashville = true;

    var divs = get_divs_of_song(song_div.id, ["chord", "key"]);
    var key = null;

    for ( var i=0; i<divs.length; i++ )
        {
        var div = divs[i];
        if ( div.classList.contains("key") )
            {
            key = div.innerHTML.trim();
            // alert("Key change: " + key);
            // alert(get_scale(key));
            }
        else
            {
            if ( !key ) { key = get_root(div.innerHTML.trim()); }
            nashville_chord(div, key);
            }
        }
    }
//}}}

//{{{ function: get_artist_album_song
function get_artist_album_song()
    {
    // get topmost song title:
    var song_div = topmost_song();
    var song_title = song_div.title

    // get artist and album name from page title:
    var all_divs = document.getElementsByTagName("title");
    var page_title = all_divs[0].innerHTML;
    var splits = page_title.split(":");
    var artist = splits[1].trim();
    var album = splits[2].trim();

    return [ artist, album, song_title ];
    }
//}}}
//{{{ function: play_current_song
function play_current_song(bootlegs=false)
    {
    var y_offset = window.pageYOffset;
    var artist_album_song = get_artist_album_song();

    var artist = artist_album_song[0];
    var album = artist_album_song[1];
    var song = artist_album_song[2];

    if ( y_offset == 0 )
        {
        // top of page => album
        var artist = artist.replace(" ", "%20");
        var album = album.replace(" ", "%20");
        var song = null;
        }
    else
        {
        if ( artist == "Misc" )
            {
            var artist = "";
            if ( song.includes("(") )
                { song = song.replace(/\([^)]+\)$/, ""); }
            }

        var artist = artist.replace(" ", "%20");
        var album = album.replace(" ", "%20");
        var song = song.replace(" ", "%20");

        var album = null; /// CURRENTLY UNSUPPORTED BY LAUDABLE
        }

    var url = "http://127.0.0.1:5000/laudable"
            
    if ( artist && album && song ) 
        { url += "?artist=" + artist + "&album=" + album + "&song=" + song }
    else if ( artist && song )
        { url += "?artist=" + artist + "&song=" + song }
    else if ( artist && album )
        { url += "?artist=" + artist + "&album=" + album }
    else if ( song )
        { url += "?song=" + song }

    if ( bootlegs )
        { url += "&bootlegs=true" }

    fetch(url);
    }
//}}}

//{{{ function: navigate_up
function navigate_up()
    {
    // top of screen -> artist page -> index

    var url = window.location.pathname;
    var filename = url.substring(url.lastIndexOf('/')+1);
    var subs = filename.split("#")[0].split("_");
    var not_artists = [ "folk_index.html" ];
    var back = "index.html";

    if ( document.body.scrollTop > 0 )
        {
        window.scrollTo(0,0);
        return;
        }

    if ( subs.length > 1 && !not_artists.includes(filename) )
        {
        back = subs[0] + ".html";
        }

    window.location.href = back;
    return;
    }
//}}}

//{{{ function: lyrics_only
function lyrics_only() {
    var div = topmost_song();

    if ( div.hasOwnProperty("lyrics_only") )
        {
        div.innerHTML = div.raw;
        delete div.lyrics_only;
        return;
        }

    div.lyrics_only = true;

    var lines = div.innerHTML.split(/\r?\n|\r|\n/g);
    var newlines = [];

    ignore_divs = [ "chord", "capo", "tabline", "fingering", "tuning", "comment" ]

    for ( var i=0; i<lines.length; i++ )
        {
        var line = lines[i];
        var keep = true;
    
        for ( var j=0; j<ignore_divs.length && keep; j++ )
            {
            if ( line.includes("<div class=\"" + ignore_divs[j] + "\"") )
                {
                // ignore unwanted div lines
                keep = false;
                }
            }

        if ( keep && line.trim() == "" && newlines.length == 0 )
            {
            // ignore whitespace at the top
            keep = false;
            }

        if ( keep )
            { 
            newlines.push(line);
            }
        }

    div.innerHTML = newlines.join("\n");
    }
//}}}
//{{{ function: theory_popup
function theory_popup(harp=false) 
    {
    var target = "theory.html";

    if ( !window.location.pathname.includes(target) )
        {
        if ( harp ) 
            { 
            target = target + "#DiatonicHarmonicaPositions"; 
            }

        // pass wprops as third argument to force new window; but more annoying than expected
        var wprops = "location=yes,height=570,width=820,scrollbars=yes,status=yes";
        window.open(target, "_blank");
        }
    }
//}}}

//{{{ function: next_or_previous
function next_or_previous(next)
    {
    var element = null;
    if ( next ) 
        { element = document.getElementById("next"); }
    else        
        { element = document.getElementById("prev"); }
    window.location.href = element.href;
    }
//}}}

//{{{ function: assign_shortcuts
function assign_shortcuts()
    {
    shortcut.add("a",function() { show_all_versions() });
    shortcut.add("d",function() { goto_dylan() });
    shortcut.add("h",function() { cycle_versions(topmost_song().id, false) });
    shortcut.add("j",function() { transpose_topmost_song(false) });
    shortcut.add("k",function() { transpose_topmost_song(true)  });
    shortcut.add("l",function() { cycle_versions(topmost_song().id, true) });
    shortcut.add("v",function() { cycle_versions(topmost_song().id, true) });
    //shortcut.add("n",function() { nashville_system()  });
    shortcut.add("p",function() { play_current_song()  });
    shortcut.add("o",function() { play_current_song(true)  });
    shortcut.add("u",function() { navigate_up()  });
    shortcut.add("s",function() { toggle_sort() });
    //shortcut.add("t",function() { theory_popup(true) });
    shortcut.add("z",function() { lyrics_only() });
    shortcut.add("f",function() { prompt_for_search() });
    shortcut.add(",",function() { next_or_previous(false) }); // <
    shortcut.add(".",function() { next_or_previous(true) });  // >

    var ss = get_style_cookie();
    if ( ss ) { cycle_styles(ss); }

    var version_anchor = window.location.href.match(/\?v=(\d+)#(\w+)/);
    if ( version_anchor )
        {
        var version = version_anchor[1];
        var anchor = version_anchor[2];

        // jump to anchor
        location.replace("#" + anchor)

        // set version from url parameter
        var song_id = topmost_song().id
        set_version_of_song(song_id, version);
        set_version_selector(song_id, version);
        }

    if ( window.location.pathname.includes("songs.html") )
        {
        do_search();
        }

    }
//}}}

//{{{ function: toggle_artist_sort
function toggle_artist_sort()
    {
    var div = document.getElementsByClassName('col4')[0];
    var lines = div.innerHTML.split(/\r?\n|\r|\n/g);

    var sorted_by_name = lines.slice();
    sorted_by_name.sort();

    var sorted_by_count = lines.slice();
    sorted_by_count.sort( function(a, b) {
        var m_a = a.match(/(\d+)\/(\d+)/);
        var m_b = b.match(/(\d+)\/(\d+)/);

        if ( m_a && m_b ) { return Number(m_b[1]) - Number(m_a[1]); }
        else if ( m_a ) { return -1; }
        else if ( m_b ) { return 1; }
        } );

    if ( lines[0] == sorted_by_count[0] ) { lines = sorted_by_name;  }
    else                                  { lines = sorted_by_count; }

    div.innerHTML = lines.join("\n");
    }
//}}}
//{{{ function: toggle_folk_sort
function toggle_folk_sort()
    {
    var div = document.getElementsByTagName('tbody')[0];
    var lines = div.innerHTML.split("</tr>");

    if ( !div.hasOwnProperty("raw") )
        { div.raw = lines }

    var child = lines.slice();
    var roud = lines.slice();

    child.sort( function(a, b) {
        var m_a = a.match(/Child (\d+)/);
        var m_b = b.match(/Child (\d+)/);

        if ( m_a && m_b ) { return Number(m_a[1]) - Number(m_b[1]); }
        else if ( m_a ) { return -1; }
        else if ( m_b ) { return 1; }
        } );

    roud.sort( function(a, b) {
        var m_a = a.match(/Roud (\d+)/);
        var m_b = b.match(/Roud (\d+)/);

        if ( m_a && m_b ) { return Number(m_a[1]) - Number(m_b[1]); }
        else if ( m_a ) { return -1; }
        else if ( m_b ) { return 1; }
        } );

    if      ( lines[0] == child[0] ) { lines = roud;  }
    else if ( lines[0] == roud[0]  ) { lines = div.raw; }
    else                             { lines = child; }

    div.innerHTML = lines.join("</tr>");

    }
//}}}
//{{{ function: toggle_sort
function toggle_sort()
    {

    if ( document.getElementsByClassName('col4').length > 0 ) 
        { toggle_artist_sort(); return; }

    if ( document.getElementsByTagName('tbody').length > 0 ) 
        { toggle_folk_sort(); return; }

    }
//}}}

//{{{ function: handle_horizontal_swipe
function handle_horizontal_swipe() 
    {
    var tolerance = 100;
    // alert(["X:", touchstartX, touchendX]);
    // alert(["Y:", touchstartY, touchendY]);

    var top_of_screen = touchstartY < 200 && touchendY < 200;
    var swiped_left = touchstartX - touchendX > tolerance;
    var swiped_right = touchendX - touchstartX > tolerance;

    if ( top_of_screen )
        {
        if ( swiped_left )  { next_or_previous(true); }
        if ( swiped_right ) { next_or_previous(false);  }
        }
    else
        {
        var song = topmost_song();
        if ( swiped_left )  { cycle_versions(song.id, true);  }
        if ( swiped_right ) { cycle_versions(song.id, false); }
        }
    }
//}}}

//{{{ function: toggle_settings_menu
function toggle_settings_menu()
    {
    var div = document.getElementsByClassName('settings-menu')[0];

    if ( div.style.display == "block" )
        { div.style.display = "none"; }
    else
        { div.style.display = "block"; }
    }
//}}}
//{{{ function: hide_settings_menu
function hide_settings_menu()
    {
    var div = document.getElementsByClassName('settings-menu')[0];
    if ( div.style.display == "block" )
        { div.style.display = "none"; }
    }
//}}}

//{{{ function: prompt_for_search
function prompt_for_search()
    {
    var pattern = prompt("Enter search pattern (searches artist, song and album names):");
    window.location.href = "songs.html?search=" + pattern.replace(" ", "+");
    }
//}}}
//{{{ function: do_search
function do_search()
    {
    var pattern = window.location.href.match(/\?search=([A-Za-z0-9+]+)/);
    if ( pattern )
        {
        pattern = pattern[1]
        pattern = pattern.replace("+", " ");
        pattern = pattern.trim()

        var lines = document.body.innerHTML.split(/\r?\n|\r|\n/g);
        var matches = [];

        for ( var i=0; i<lines.length; i++ )
            {
            if ( lines[i].toLowerCase().includes(pattern.toLowerCase()) )
                {
                matches.push(lines[i]);
                }
            }

        if ( matches.length == 0 )
            {
            prompt_for_search();
            }
        else if ( matches.length == 1 )
            {
            // jump to single match
            var url = matches[0].match( RegExp( "(\\w+\\.html#\\w+)" ) )
            window.location.href = url[0];
            }
        else
            {
            // replace body with matches

            var header = "<h2>";
            header += "<a href=index.html>Song Search Results</a> "
            header += "<a href=songs.html>(Clear)</a>";
            header += "</h2><hr>";

            matches.unshift(header);

            document.body.innerHTML = matches.join("\n<br>");
            }
        }
    }
//}}}

let touchstartX = 0
let touchendX = 0
let touchstartY = 0
let touchendY = 0

document.addEventListener('touchstart', e => {
    touchstartX = e.changedTouches[0].screenX
    touchstartY = e.changedTouches[0].screenY
    })

document.addEventListener('touchend', e => {
    touchendX = e.changedTouches[0].screenX
    touchendY = e.changedTouches[0].screenY
    handle_horizontal_swipe()
    })

document.addEventListener('DOMContentLoaded', reset_version_selectors, false);
window.onload = assign_shortcuts;
document.write('<script src="shortcut.js"></script>');
document.onclick = function(e) {
    if ( e.target.className == "settings-icon" )
        { toggle_settings_menu(); }
    else if ( e.target.parentElement.className == "settings-menu" )
        { }
    else
        { hide_settings_menu(); }
    }

