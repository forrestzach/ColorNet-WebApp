import React, {useState, useEffect} from 'react';
import Main from './components/FileUpload.js';

function App() {
  const [currentTime, setCurrentTime] =  useState(0);

  useEffect(() => {
    fetch('/api/time').then(res => res.json()).then(data => { setCurrentTime(data.time); });
      }, []);


  return(
    <div>
    <h1>ColorNet</h1>
    <Main />
    
    {/* <p> The current time is {currentTime}.</p> */}
    {console.log("The current time is " + currentTime)}
    </div>

  );
}

export default App;