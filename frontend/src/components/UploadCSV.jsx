import {useState, useEffect} from "react";
import { Pie, Bar, Line, Scatter } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
} from 'chart.js';
import Footer from "./Footer";
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    PointElement,
    LineElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
);

const AUTH_HEADERS = {
  Authorization: "Basic " + btoa("admin:chemicaladmin123")    //basic auth for the backend.
};


function UploadCSV(){
    const [file,setFile] = useState(null);  //store selected file
    const [summary,setSummary] = useState(null);  //store summary received from backend
    const [loadingSummary,setLoadingSummary] = useState(false);  //track loading state
    const[uploading,setUploading] = useState(false);  //track uploading state
    const [uploadSuccess, setUploadSuccess] = useState(false); //only after this we can download PDF

    const[PTdata,setPTdata] = useState([]); //store pressure temperature data just for chart

    const handleFileChange = (e) => {   //in case user choses other file.
        setFile(e.target.files[0]);
        setSummary(null);  //reset summary when new file is selected
        setPTdata([]); //reset PT data
        setUploadSuccess(false); //reset upload success
    };

    const handleUpload = async () => {  //upload file to backend
        if(!file) return;
        
        const formData = new FormData();
        formData.append('file',file);
        try{
            setUploading(true); //start uploading
            const response = await fetch("http://127.0.0.1:8000/api/equipment/upload/",{
                method:'POST',
                headers: AUTH_HEADERS,
                body:formData,
            });
            const data = await response.json();
            setSummary(data);
        }
        catch(error){
            console.error("Error uploading file:",error);
        }
        finally{
            setUploading(false); //end uploading
        }
    };

    const fetchsummary = async () => {  //fetch summary from backend
        try{
            setLoadingSummary(true); //start loading
            const response = await fetch(
                "http://127.0.0.1:8000/api/equipment/summary/",
                {headers: AUTH_HEADERS}
            );
            const data = await response.json();
            // console.log("SUMMARY FROM BACKEND:", data);
            setSummary(data); //store summary data

        }
        catch(error){
            console.error("Error fetching summary:",error);
        }
        finally{
            setLoadingSummary(false); //end loading
        }
    };

    const fetchpressuretemperature = async () => {
        try{
            const response = await fetch(
                "http://127.0.0.1:8000/api/equipment/pressure-temperature/",
                {headers: AUTH_HEADERS}
            );
            const data = await response.json();
            setPTdata(data);
        }
        catch(error){
            console.error("Error fetching pressure temperature data:",error);
        }
    };
    
    useEffect(() => {
        if(summary){
            fetchpressuretemperature();
        }
    }, [summary]);


    let chartData1 = null;
    let chartData2 = null;
    let chartData3 = null;
    if(summary && summary.type_distribution){
        const labels1 = Object.keys(summary.type_distribution);
        const count1 = Object.values(summary.type_distribution);

        chartData1 = {
            labels: labels1,
            datasets: [
                {
                    label: 'Equipment Count',
                    data: count1,
                    backgroundColor: [
                        '#1F77B4',
                        '#FF7F0E',
                        '#2CA02C',
                        '#D62728',
                        '#9467BD',
                        '#8C564B',
                    ]
                }
            ]
        };

        const labels2 = ['avg_flowrate','avg_pressure','avg_temperature'];
        chartData2 = {
            labels: labels2,
            datasets: [
                {
                    label: 'Average Metrics',
                    data: [summary.avg_flowrate, summary.avg_pressure, summary.avg_temperature],
                    backgroundColor: [
                        '#1f77b4',
                        '#ff7f0e',
                        '#2ca02c',
                    ]
                }
            ]
        }

        if(PTdata.length > 0){
            chartData3 = {
                labels: PTdata.map(item => item.pressure),
                datasets: [
                    {
                        label: 'Pressure(x-axis) Vs Temperature(y-axis)',
                        data: PTdata.map(item => item.temperature),
                        borderColor: 'rgba(75,192,192,1)',
                        fill: true,
                    }
                ]
            }
        }
    }
    useEffect(() => {
            if (summary && summary.type_distribution) {
                setUploadSuccess(true);
            }
        }, [summary]);


    const downloadPDF = async () => {
        try {
            const response = await fetch(
                "http://127.0.0.1:8000/api/equipment/report/pdf/",
                {headers: AUTH_HEADERS}
            );

            if (!response.ok) {
                throw new Error("Failed to download PDF");
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = "Equipment_Report.pdf";
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        }
        catch (error) {
            console.error(error);
            alert("PDF download failed");
        }
    };


    
    return (
        <div className="container">
            <div className="card">
                <h1>Chemical Equipment Parameter Visualizer</h1>
                <h2 className="title">Upload CSV File</h2>

                <div className="upload-section">
                    <input className="file-input" type="file" accept=".csv" onChange={handleFileChange}/>
                    {/* {file && <p className="file-name">Selected File: {file.name}</p>} */}

                    <button className="button" onClick={handleUpload} disabled={!file || uploading}>
                        {uploading ? "Uploading..." : "Upload"}
                    </button>
                </div>

                {loadingSummary && <p className="loading">Loading summary...</p>}

                {summary && (
                    <div className="summary-section">
                        <h3>Summary</h3>

                        <div className="summary-grid">
                            <div className="summary-item">
                                <span>Total Equipment: </span>
                                <strong>{summary.total_equipment}</strong>
                            </div>

                            <div className="summary-item">
                                <span>Avg Flowrate: </span>
                                <strong>{summary.avg_flowrate}</strong>
                            </div>

                            <div className="summary-item">
                                <span>Avg Pressure: </span>
                                <strong>{summary.avg_pressure}</strong>
                            </div>

                            <div className="summary-item">
                                <span>Avg Temperature: </span>
                                <strong>{summary.avg_temperature}</strong>
                            </div>
                        </div>

                        <h4>Equipment Type Distribution</h4>

                        {summary.type_distribution && (
                            <div className="equipment-grid">
                                {Object.entries(summary.type_distribution).map(([type, count]) => (
                                <div className="equipment-card" key={type}>
                                    <span className="equipment-type">{type}</span>
                                    <span className="equipment-count">{count}</span>
                                </div>
                                ))}
                            </div>
                        )}


                        <div className="chart-section">
                            <h3>Equipment Type Counts</h3>
                            {chartData1 && (
                            <div className="chart-box">
                                <Pie data={chartData1} />
                            </div>
                            )}
                        </div>

                        <div className="chart-section">
                            <h3>Average Metrics</h3>
                            {chartData2 && (
                            <div className="chart-box">
                                <Bar data={chartData2} />
                            </div>
                            )}
                        </div>
                    </div>
                )}

                {chartData3 && (
                    <div className="chart-section">
                        <h3>Pressure vs Temperature</h3>
                        <div className="chart-box">
                            <Scatter data={chartData3} />
                        </div>
                    </div>
                )}

                <div className="action-section">
                    <button className="button secondary" onClick={downloadPDF} disabled={!uploadSuccess}>
                        Download PDF Report
                    </button>
                </div>
                <Footer />
            </div>
        </div>
        );

}
export default UploadCSV;