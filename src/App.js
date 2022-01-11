import './App.css';
import React, { useState, useRef } from 'react';


function App() {
  const args = JSON.parse(document.getElementById("data").text);
  const [Artistid, setArtistid] = useState(args.artist_ids);
  const textInput = useRef(null);

  function addArtistid() {
    let newItem = textInput.current.value;
    let updatedArtists = [...Artistid, newItem];
    setArtistid(updatedArtists);
    textInput.current.value = "";
    console.log(updatedArtists);
  }

  function deleteArtistid(artist_Del) {
    let updatedArtists = [...Artistid];
    const index = updatedArtists.indexOf(artist_Del);
    if (index > -1) {
      updatedArtists.splice(index, 1);
    }
    setArtistid(updatedArtists);
  }

  function saveArtistid() {
    console.log(JSON.stringify({ "artist_list": Artistid }))
    fetch('/save-songs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ "artist_list": Artistid }),
    }).then(response => response.json()).then(data => {
        console.log(data)
        setArtistid(data.artist_server);
      });
  }

  return (
    <>
      <h1>{args.username}'s Song Explorer</h1>
      {(args.has_artists_saved) ? (
        <>
          <h2>{args.song_name}</h2>
          <h3>{args.song_artist}</h3>
          <div>
            <img src={args.song_image_url} width={300} height={300} />
          </div>
          <div>
            <audio controls>
              <source src={args.preview_url} />
            </audio>
          </div>
          <a href={args.genius_url}> Click here to see lyrics! </a>
          <h1>Here are the artists you have saved:</h1>
          <ul>
            {Artistid.map((i) => (
              <li key={i.id}>
                {i} <button type="button" onClick={() => deleteArtistid(i)}> X </button>
              </li>
            ))}
          </ul>
        </>) :
        (<h2>Looks like you don't have anything saved! Use the form below!</h2>)
      }
      <h1>Save a favorite artist ID for later:</h1>
      <input ref={textInput} type="text" required />
      <button onClick={addArtistid}>Add an artist!</button>
      <h2>Click here to save!</h2>
      <button onClick={saveArtistid}>Save</button>
      <h3>Please reload page to see new artist</h3>

    </>
  );
} export default App;