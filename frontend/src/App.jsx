import UploadCSV from "./components/UploadCSV.jsx";
import Footer from "./components/Footer.jsx";
import './App.css';


function App(){
  return(
    <div className="app-container">
      <div className="header">
        {/* <h1>Chemical Equipment Parameter Visualizer</h1> */}
      </div>
    <UploadCSV />
    </div>

  );
}
export default App;
