import {Link} from "react-router-dom";

export default function Header() {
    return(
        <header>
            <Link to="/" className="logo">Spark</Link>
            <nav>
                <Link to="/login">Login</Link>
                <Link to="/signup">SignUp</Link>
            </nav>
        </header>
    );
}