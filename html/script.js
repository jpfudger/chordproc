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

//{{{ function: toggle_multicolumn_topmost_song
function toggle_multicolumn_topmost_song()
    {
    var song_div = topmost_song();

    // read the column-count from css
    var n_cols = getComputedStyle(song_div).columnCount;

    // then update it 
    if ( n_cols == 1 )
        {
        song_div.style.columnCount = 2;
        }
    else if ( n_cols == 2 )
        {
        song_div.style.columnCount = 3;
        }
    else
        {
        song_div.style.columnCount = 1;
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
    if ( d.classList.contains("fixed") ) 
        {
        // currently this is only used for harp key w.r.t. capo
        return;
        }

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
//{{{ function: enharmonic_note
function enharmonic_note(note) {
    var upper_note = note[0].toUpperCase() + note[1];
    var notes_sharp = get_notes("A", true);
    var notes_flat = get_notes("A", false);

    var index = notes_sharp.indexOf(upper_note);
    var new_note = note;

    if ( index != -1 )
        {
        new_note = notes_flat[index];
        }
    else
        {
        index = notes_flat.indexOf(upper_note);
        new_note = notes_sharp[index];
        }

    if ( upper_note != note )
        {
        new_note = new_note.toLowerCase();
        }

    return new_note;
    }
//}}}
//{{{ function: swap_enharmonics
function swap_enharmonics() {
    var song = topmost_song();
    var divs = get_divs_of_song(song.id, ["chord", "key"]);

    for ( var i=0; i<divs.length; i++) {
        var chord = divs[i].innerHTML;
        var root = get_root(chord);
        var bass = get_bass(chord);

        var new_root = null;
        var new_bass = null;

        // alert(chord + " (" + root + ") (" + bass + ")");

        if ( root != null && root.length == 2 )
            {
            new_root = enharmonic_note(root);
            // if ( root == new_root ) { new_root == null; }
            }

        if ( bass != null && bass.length == 2 )
            {
            new_bass = enharmonic_note(bass);
            // if ( bass == new_bass ) { new_bass == null; }
            }

        if ( new_root != null || new_bass != null )
            {
            // alert("->" + new_root + ", " + new_bass);
            var new_chord = chord;
            if ( new_root != null ) { new_chord = new_chord.replace(RegExp("^" + root), new_root); }
            if ( new_bass != null ) { new_chord = new_chord.replace(RegExp("/" + bass), "/" + new_bass); }
            // alert(new_chord);
            divs[i].innerHTML = new_chord;
            }

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
//{{{ function: toggle_capo
function toggle_capo(capo_link_div) {

    // The capo div is within a comment div and maybe a span.
    // Because we don't know which, keep trying until we find a chords div.

    if ( capo_link_div.parentElement.style.textDecoration == "line-through" )
        {
        capo_link_div.parentElement.style.textDecoration = "none";
        }
    else
        {
        capo_link_div.parentElement.style.textDecoration = "line-through";
        }

    var song_div = capo_link_div;

    while ( !song_div.classList.contains("chords") )
        {
        song_div = song_div.parentElement;
        }

    // Remember the capo_link_div is not the same as the capo_div!

    var capo_div = song_div.getElementsByClassName("capo")[0];
    var capo_numeral = capo_div.innerHTML;
    var capo_decimal = numeral_to_decimal(capo_numeral);
    var capo_delta = capo_decimal;

    if ( !song_div.hasOwnProperty("original_capo") )
        {
        song_div.original_capo = capo_decimal;
        }

    if ( capo_decimal == 0 && song_div.original_capo != capo_decimal )
        {
        capo_delta = -song_div.original_capo;
        }

    for ( var i=Math.abs(capo_delta); i>0; i-- ) 
        {
        transpose_song(song_div.id, capo_delta > 0);
        }

    // alert(capo_decimal);
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
    var selector = document.getElementById( song_index + ".version")
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
        // must distinguish between .version and .name_name selectors
        if ( selectors[i].id.endsWith(".version") )
            {
            selectors[i].value = 0;
            }
        }
    }
//}}}
//{{{ function: set_version_selector
function set_version_selector(song_id, index)
    {
    var selector = document.getElementById(song_id + ".version");
    selector.value = index;
    }
//}}}

//{{{ function: jump_to_song_link
function jump_to_same_name(song_index)
    {
    // get selector for song_index
    // get current option value
    // follow its url (data-link)
    var selector = document.getElementById( song_index + ".same_names");
    var option = selector.options[selector.selectedIndex];
    var url = option.dataset.link;
    window.location.href = url;
    return;
    }
//}}}
//{{{ function: jump_to_page
function jump_to_page(page)
    {
    var url = window.location.pathname;
    
    if ( url.endsWith("/") )
        {
        url += page;
        }
    else if ( url.endsWith(".html") )
        {
        url = url.replace(RegExp("\\w+\\.html.*"), page);
        }
    else 
        {
        alert("Cannot add page to url " + url);
        }

    window.location.href = url;
    return;
    }
//}}}
//{{{ function: jump_to_artist_index
function jump_to_artist_index()
    {
    var url = window.location.pathname;
    var array = url.match( RegExp("\\w+\\.html") );
    var artist = array[0].split("_")[0];

    url = url.replace(RegExp("\\w+\\.html.*"), artist + ".html");
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
    var song = get_divs_of_song(song_index, ["chords"])[0];
    var theory = window.location.href.includes("/theory.html");

    var capo_divs = get_divs_of_song(song_index, ["capo"]);
    var capo_div = capo_divs.length == 1 ? capo_divs[0] : null;

    // add capo line if not present (but not for the theory page)
    if ( !theory && !capo_div )
        {
        newline = "<br><div class=comment><a class=capo_button onclick='toggle_capo(this);'>Capo</a>: <div class=capo>0</div> </div><br>";
        song.innerHTML = newline + song.innerHTML;
        }

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
function get_scale(key, for_note=null)
    {
    var scale = [ key ];
    var intervals = [ 2, 2, 1, 2, 2, 2, 1 ];

    var prefer_sharp = key.includes("#");

    if ( for_note )
        {
        prefer_sharp = for_note.includes("#");
        }

    var notes = get_notes(key, prefer_sharp);
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

    if ( !root )
        {
        // e.g. a pure bass note: /b
        return;
        }

    var scale = get_scale(key, root);
    var degree = scale.indexOf(root) + 1;
    var accidental = "";

    if ( !degree )
        {
        // alert(chord_div.innerHTML + ": can't find " + root + " in the " + key + " scale");
        var tmp_root = root;
        if ( root.endsWith("#") )
            {
            tmp_root = tmp_root.substring(0, tmp_root.length-1);
            scale = get_scale(key, tmp_root);
            degree = scale.indexOf(tmp_root) + 1;
            accidental = "#"
            }
        else if ( tmp_root.endsWith("b") )
            {
            tmp_root = tmp_root.substring(0, tmp_root.length-1);
            scale = get_scale(key, tmp_root);
            degree = scale.indexOf(tmp_root) + 1;
            accidental = "b"
            }
        else
            {
            tmp_root += "#"
            scale = get_scale(key, tmp_root);
            degree = scale.indexOf(tmp_root) + 1;
            accidental = "#"
            }
        }

    var numeral = decimal_to_numeral(degree) + accidental;

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
    var artist = splits[0].trim();
    var album = splits[1].trim();

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
        artist = artist.replace(" ", "%20");
        album = album.replace(" ", "%20");
        song = null;
        }
    else
        {
        if ( artist == "Misc" )
            {
            artist = "";
            if ( song.includes("[") )
                { 
                song = song.replace(/\[[^)]+\]$/, "");
                }
            }

        artist = artist.replace(" ", "%20");
        album = album.replace(" ", "%20");

        song = song.split("<div")[0];
        song = song.replace(" ", "%20");

        album = null; /// CURRENTLY UNSUPPORTED BY LAUDABLE
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

    var last_line_empty = false;

    for ( var i=0; i<lines.length; i++ )
        {
        var line = lines[i];
        line = line.replace(/<.?span>/, '');
        var keep = true;
        var empty = line.trim() == "";
    
        for ( var j=0; j<ignore_divs.length && keep; j++ )
            {
            if ( line.includes("<div class=\"" + ignore_divs[j] + "\"") )
                {
                // ignore unwanted div lines
                keep = false;
                }
            }

        if ( keep && newlines.length == 0 && empty )
            {
            // ignore whitespace at the top
            keep = false;
            }

        if ( last_line_empty && empty )
            {
            keep = false;
            }

        if ( !last_line_empty && empty )
            {
            line += "</span>";
            }

        if ( keep )
            { 
            var unindented = line.replace(/^\s+/, '');

            if ( line.length - unindented.length < 4 )
                {
                line = unindented;
                }

            // ensure only one space between words
            line = line.replace(/(?<=\S)\s+/g, ' ');

            if ( last_line_empty && !empty )
                {
                line = "<span>" + line;
                }

            newlines.push(line);
            }

        if ( keep ) { last_line_empty = empty; }
        }

    div.innerHTML = "<br>" + newlines.join("\n");
    }
//}}}
//{{{ function: toggle_modulation
function toggle_modulation() {
    var div = topmost_song();

    if ( div.hasOwnProperty("modulation_cancelled") )
        {
        div.innerHTML = div.raw;
        delete div.modulation_cancelled;
        return;
        }

    var chords = div.getElementsByClassName("chord");
    var key = null;
    var original_key = null;
    var new_key = null;

    var interval = 0;

    for ( var i=0; i<chords.length; i++ )
        {
        var chord = chords[i];

        if ( chord.classList.contains("key") )
            {

            if ( chord.parentElement.innerHTML.includes("Modulate to") )
                {
                chord.parentElement.style.textDecoration = "line-through";
                }

            new_key = chord.innerHTML;

            if ( key )
                {
                var notes = get_notes(key);
                interval += notes.indexOf(new_key) - notes.indexOf(key);
                chord.innerHTML = original_key;
                }
            else
                {
                original_key = new_key;
                }

            key = new_key;
            }
        else if ( interval != 0 )
            {
            // alert(chord.innerHTML + " increment " + interval.toString() );

            var up = Math.sign(interval) == -1;
            var abs_interval = Math.abs(interval);

            for ( var j=0; j<abs_interval; j++ )
                {
                cycle_chord_div(chord, up);
                }
            }
        }

    // do this at the end in case something breaks
    div.modulation_cancelled = true;

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
    var opts = { "disable_in_input": true };
    shortcut.add("a",function() { show_all_versions() }, opts);
    shortcut.add("c",function() { toggle_multicolumn_topmost_song() }, opts);
    shortcut.add("d",function() { jump_to_page("bobdylan.html") }, opts);
    shortcut.add("e",function() { swap_enharmonics() }, opts);
    shortcut.add("f",function() { prompt_for_song_search() }, opts);
    // shortcut.add("shift+f",function() { prompt_for_song_search(true) }, opts); // same artist
    shortcut.add("h",function() { cycle_versions(topmost_song().id, false) }, opts);
    shortcut.add("i",function() { jump_to_page("index.html") }, opts);
    shortcut.add("shift+i",function() { jump_to_artist_index() }, opts);
    shortcut.add("j",function() { transpose_topmost_song(false) }, opts);
    shortcut.add("k",function() { transpose_topmost_song(true)  }, opts);
    shortcut.add("l",function() { cycle_versions(topmost_song().id, true) }, opts);
    shortcut.add("m",function() { toggle_modulation() }, opts);
    shortcut.add("n",function() { nashville_system() }, opts);
    shortcut.add("p",function() { play_current_song() }, opts);
    shortcut.add("shift+p",function() { play_current_song(true)  }, opts); // inc. bootlegs
    shortcut.add("r",function() { random_song() }, opts);
    shortcut.add("shift+r",function() { random_song(true) }, opts); // same artist
    shortcut.add("s",function() { toggle_sort() }, opts);
    // shortcut.add("t",function() { prompt_for_tuning_search() }, opts); // triggers on F5!?
    shortcut.add("shift+t",function() { jump_to_page("theory.html") }, opts);
    shortcut.add("u",function() { navigate_up() }, opts);
    shortcut.add("v",function() { cycle_versions(topmost_song().id, true) }, opts);
    shortcut.add("w",function() { prompt_for_word_search() }, opts);
    shortcut.add("z",function() { lyrics_only() }, opts);
    shortcut.add(",",function() { next_or_previous(false) }, opts); // <
    shortcut.add(".",function() { next_or_previous(true) }, opts);  // >
    shortcut.add("escape",function() { hide_search_box() }); // no opts, so it works in input box

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
        do_song_search();
        }

    if ( window.location.pathname.includes("tunings.html") )
        {
        do_tuning_search();
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

//{{{ function: get_artist_from_url
function get_artist_from_url()
    {
    var ignore = [ "index", "songs", "folk", "tunings", "theory" ];

    var artist = window.location.href.match(/([a-z0-9]+)_/);

    if ( !artist )
        {
        // main artist page
        artist = window.location.href.match(/([a-z0-9]+)\.html/);
        }

    if ( artist )
        {
        artist = artist[1];

        if ( ignore.indexOf(artist) != -1 )
            {
            artist = null;
            }

        }

    return artist;
    }
//}}}
//{{{ function: random_song
function random_song(same_artist=false)
    {
    var url = "songs.html?random=1";

    if ( same_artist )
        {

        var artist = get_artist_from_url();

        if ( artist )
            {
            url += "?artist=" + artist;
            }

        }

    window.location.href = url;
    }
//}}}
//{{{ function: prompt_for_song_search
function prompt_for_song_search(same_artist=false)
    {
    var search_container = document.getElementById("search-container");
    var search_div = document.getElementById("search");
    var search_pattern = document.getElementById("pattern");

    hide_settings_menu();

    search_pattern.value = "";
    search_container.style.display = "block";
    search_pattern.focus();

    search_pattern.addEventListener("keypress", function(event)
        {
        // alert(event.key);
        if ( event.key === "Enter" )
            {
            if ( search_pattern.value.trim() != "" )
                {
                do_button_search(same_artist);
                }
            }
        else if ( event.key === "`" )
            {
            search_container.style.display = "none";
            }
        } );

    }
//}}}
//{{{ function: prompt_for_word_search
function prompt_for_word_search()
    {
    var pattern = prompt("Enter word:");
    window.location.href = "songs.html?word=" + pattern.replace(/ /g, "+");
    }
//}}}
//{{{ function: do_song_search
function do_song_search()
    {
    var pattern = window.location.href.match(/\?search=([^?]*)/);
    var random  = window.location.href.match(/\?random=1/);
    var artist  = window.location.href.match(/\?artist=([^?]*)/);
    var word  = window.location.href.match(/\?word=([^?]*)/);
    if ( pattern )
        {
        pattern = pattern[1];
        pattern = pattern.replace(/\+/g, " ");   // +   -> space
        pattern = pattern.replace(/\%22/g, '"'); // %22 -> "
        pattern = pattern.replace(/\%27/g, "'"); // %27 -> '
        pattern = pattern.trim()

        var results = document.getElementById("results");
        var lines = results.innerHTML.split(/\r?\n|\r|\n/g);

        if ( artist )
            {
            artist = artist[1];
            lines = lines.filter((line) => line.match( RegExp(artist + "_") ) );
            }

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
            prompt_for_song_search();
            }
        else if ( matches.length == 1 )
            {
            // jump to single match
            var url = matches[0].match( RegExp( "(\\w+\\.html#\\w+)" ) )
            window.location.href = url[0];
            }
        else
            {
            // update title and body
            var h2 = document.getElementsByTagName('h2')[0];
            h2.innerHTML = "<a href=songs.html>Song Search Results</a>";

            if ( matches.length > 50 )
                {
                matches = [].concat( [ "<div class=\"col2\">" ], matches, [ "</div>" ]);
                }

            results.innerHTML = matches.join("\n<br>");
            }
        }
    else if ( random )
        {
        var results = document.getElementById("results");
        var lines = results.innerHTML.split(/\r?\n|\r|\n/g);

        if ( artist )
            {
            artist = artist[1];
            lines = lines.filter((line) => line.match( RegExp(artist + "_") ) );
            }

        var random_line = lines[Math.floor(Math.random() * lines.length)];
        var url = random_line.match( RegExp( "(\\w+\\.html#\\w+)" ) )
        //alert(url[0]);
        window.location.href = url[0];
        }
    else if ( word )
        {
        word = word[1];
        word = word.replace(/\+/g, " ");   // +   -> space
        word = word.replace(/\%22/g, '"'); // %22 -> "
        word = word.replace(/\%27/g, "'"); // %27 -> '
        word = word.trim();

        var words = get_concordance();
        
        for ( var i=0; i<words.length; i++ )
            {

            if ( words[i].startsWith(word + " :") )
                {
                var matches = words[i].split(" : ")[1].split(" | ");

                for ( var j=0; j<matches.length; j++ )
                    {
                    var song = matches[j];
                    song = song.replace(/ /g, "+");   // +   -> space
                    song = song.replace(/\%22/g, '"'); // %22 -> "
                    song = "<a href=songs.html?search=" + song + ">" + matches[j] + "</a>";
                    matches[j] = song;
                    }

                var results = document.getElementById("results");
                results.innerHTML = matches.join("\n<br>");
                }

            }

        }
    }
//}}}
//{{{ function: do_button_search
function do_button_search(same_artist=false)
    {
    var url = "songs.html";
    var msg = "Enter search pattern (searches artists/albums/songs):";

    if ( same_artist )
        {
        var artist = get_artist_from_url();

        if ( artist )
            {
            url += "?artist=" + artist;
            msg = "Enter search pattern (searches songs/albums for current artist):";
            }
        }

    var search_div = document.getElementById("search");
    var search_pattern = document.getElementById("pattern");

    var pattern = search_pattern.value;
    pattern = pattern.replace(/ /g, "+");
    url += "?search=" + pattern;
    window.location.href = url;
    }
//}}}
//{{{ function: hide_search_box
function hide_search_box()
    {
    var search_container = document.getElementById("search-container");
    search_container.style.display = "none";
    }
//}}}


//{{{ function: prompt_for_tuning_search
function prompt_for_tuning_search()
    {
    var input = prompt("Enter notes of tuning:");
    window.location.href = "tunings.html?search=" + input.replace(/ /g, "+");
    }
//}}}
//{{{ function: do_tuning_search
function do_tuning_search()
    {
    var pattern = window.location.href.match(/\?search=(.*)/);
    if ( pattern )
        {
        pattern = pattern[1];
        pattern = pattern.replace(/\+/g, " ");   // +   -> space
        pattern = pattern.replace(/\%22/g, '"'); // %22 -> "
        pattern = pattern.replace(/\%27/g, "'"); // %27 -> '
        pattern = pattern.trim()

        var chars = pattern.split("");
        var ivals = [];
        var prev_index = 0;

        for ( var i=0; i<chars.length; i++ )
            {
            var note = chars[i].toUpperCase();
            var notes = get_notes(note);
            var index = notes.indexOf(note);

            if ( i > 0 )
                {
                var rel_index = index % 12;
                if ( rel_index == 0 ) { rel_index = 12; }
                rel_index = rel_index - prev_index;
                ivals.push(rel_index);
                }

            prev_index = index;
            }

        //alert(chars);
        //alert(ivals);

        var anchor = "#";

        for ( var i=0; i<ivals.length; i++ )
            {
            anchor = anchor.concat(ivals[i].toString());
            }

        //alert(anchor);

        window.location.href = window.location.href.replace(/\?search=(.*)/g, anchor);
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

