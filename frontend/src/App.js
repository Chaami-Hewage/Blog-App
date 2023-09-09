import './App.css';
import Post from "./components/Post";

function App() {
    return (
        <main>
            <header>
                <a href="" className="logo">Spark</a>
                <nav>
                    <a href="">Login</a>
                    <a href="">Register</a>
                </nav>
            </header>
            <Post/>
            <Post/>
            <Post/>

        </main>
    );
}

export default App;
