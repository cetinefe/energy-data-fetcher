import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import { ClipLoader } from 'react-spinners'; // Import the spinner

function App() {
  const [dayRange, setDayRange] = useState('');
  const [areaType, setAreaType] = useState('');
  const [areaTypes, setAreaTypes] = useState([]);
  const [areas, setAreas] = useState([]);
  const [newData, setNewData] = useState([]);
  const [printContent1, setPrintContent1] = useState('');
  const [printContent2, setPrintContent2] = useState('');
  const [printContent3, setPrintContent3] = useState('');
  const [error, setError] = useState('');
  const [fetching, setFetching] = useState(false);
  const [loading, setLoading] = useState(false); // Add loading state
  const [fetchingAreaCodes, setFetchingAreaCodes] = useState(false); // State for fetching area codes

  const handleSubmit = async (event) => {
    event.preventDefault();
    setNewData([]);
    setPrintContent2('');
    setPrintContent3('');
    setError('');
    setFetching(true);
    setLoading(true); // Set loading to true when fetch starts

    try {
      const response = await axios.post('http://localhost:5001/fetch_data', { day_range: dayRange, area_type: areaType, areas: areas });
      if (response.data.status === 'success') {
        setFetching(true);
      } else {
        setError(response.data.message);
        setFetching(false);
        setLoading(false); // Set loading to false on error
      }
    } catch (err) {
      setError(`Error starting data fetch process: ${err.message}`);
      console.error(err);  // Log the detailed error for debugging
      setFetching(false);
      setLoading(false); // Set loading to false on error
    }
  };

  const handleFetchAreaCodes = async (event) => {
    event.preventDefault();
    setPrintContent1('');
    setError('');
    setLoading(true); // Set loading to true when fetch starts
    setFetchingAreaCodes(true); // Set fetchingAreaCodes to true when fetch starts

    try {
      const response = await axios.post('http://localhost:5001/fetch_area_codes');
      if (response.data.status === 'success') {
        setAreaTypes(response.data.area_types);
        setAreas(response.data.areas);
        setLoading(false); // Set loading to false after fetching area types
      } else {
        setError(response.data.message);
        setLoading(false); // Set loading to false on error
        setFetchingAreaCodes(false); // Set fetchingAreaCodes to false on error
      }
    } catch (err) {
      setError(`Error fetching area codes: ${err.message}`);
      console.error(err);  // Log the detailed error for debugging
      setLoading(false); // Set loading to false on error
      setFetchingAreaCodes(false); // Set fetchingAreaCodes to false on error
    }
  };

  useEffect(() => {
    let interval;
    if (fetching || fetchingAreaCodes) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get('http://localhost:5001/status');
          setPrintContent1(response.data.print_content_1);
          setPrintContent2(response.data.print_content_2);
          setPrintContent3(response.data.print_content_3);
          const insertedRows = response.data.newly_inserted_rows;
          setNewData(insertedRows);

          if (insertedRows.length > 0 || response.data.print_content_2.includes('No new data inserted.')) {
            setFetching(false);
            setLoading(false); // Set loading to false when data is fetched
            clearInterval(interval);
          }
        } catch (err) {
          setError(`Error occurred while fetching status: ${err.message}`);
          console.error(err);  // Log the detailed error for debugging
          setFetching(false);
          setLoading(false); // Set loading to false on error
          setFetchingAreaCodes(false); // Set fetchingAreaCodes to false on error
          clearInterval(interval);
        }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [fetching, fetchingAreaCodes]);

  const handleRestart = async () => {
    try {
      const response = await axios.post('http://localhost:5001/restart');
      if (response.data.status === 'success') {
        setDayRange('');
        setAreaType('');
        setNewData([]);
        setPrintContent1('');
        setPrintContent2('');
        setPrintContent3('');
        setError('Server is restarting...');
        setTimeout(() => {
          setFetching(true);
        }, 5000);
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError(`Error restarting backend: ${err.message}`);
      console.error(err);  // Log the detailed error for debugging
    }
  };

  return (
    <div className="App">
      <div className="header">
        <h1>Data Fetching Interface</h1>
      </div>
      <div className="content1">
        <label className="label">
          Please fetch "Area Types & Codes":
          <button className="button" onClick={handleFetchAreaCodes}>Fetch Area Types & Codes</button>
        </label>
      </div>
      <div className="print-contents1">
        <pre className="print-content1">{printContent1}</pre>
      </div>
      <div className="content2"> 
        <form onSubmit={handleSubmit}> 
          <label className="label">
            Please select an "Area Type" for data fetch:
            <select className="select"
              value={areaType} 
              onChange={(e) => setAreaType(e.target.value)}>
              {areaTypes.map((type, index) => (
                <option key={index} value={type}>{type}</option>
              ))}
            </select>
          </label>
          <label className="label">
            Please enter the number of days for data fetch:
            <input className="input"
              type="number"
              value={dayRange}
              onChange={(e) => setDayRange(e.target.value)}
              min="1"
              required
            />
          </label>
          <button className="button" type="submit">Fetch Data</button>
          <button className="button" type="button" onClick={handleRestart}>Restart Backend</button>
        </form>
        <div className="print-contents2">
          <pre className="print-content2">{printContent2}</pre>
          <pre className="print-content3">{printContent3}</pre>
        </div>
        {error && <p className="error">{error}</p>}
        {loading ? (
          <div className="loading">
            <ClipLoader size={30} color={"#123abc"} loading={loading} />
            <p>Loading...</p>
          </div>
        ) : (
          <>
            {newData.length > 0 ? (
              <div className="data-table">
                <h2>Newly Inserted Data</h2>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Date Area Key</th>
                      <th>Date Time</th>
                      <th>Total Load</th>
                      <th>DA Forecast</th>
                      <th>Area Code</th>
                      <th>Area Name</th>
                    </tr>
                  </thead>
                  <tbody>
                    {newData.map((row, index) => (
                      <tr key={index}>
                        <td>{row[0]}</td>
                        <td>{row[1]}</td>
                        <td>{row[2]}</td>
                        <td>{row[3]}</td>
                        <td>{row[4]}</td>
                        <td>{row[5]}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>No new data inserted.</p>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default App;
