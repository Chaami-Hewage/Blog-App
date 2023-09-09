import './App.css';
import {Route, Routes} from "react-router-dom";
import Layout from "./components/Layout";
import IndexPage from "./components/IndexPage";
import LoginPage from "./components/LoginPage";
import SignupPage from "./components/SignupPage";
import {UserContextProvider} from "./UserContext";

function App() {
    return (
        <UserContextProvider>
            <Routes>
                <Route path="/" element={<Layout/>}>
                    <Route index element={<IndexPage/>}/>
                    <Route path="/login" element={<LoginPage/>}/>
                    <Route path="/signup" element={<SignupPage/>}/>
                </Route>
            </Routes>
        </UserContextProvider>
    );
}

export default App;
