import {Link} from "react-router-dom";
import logoImage from '../assets/images/Logo-Spark.png';
import {useContext, useEffect} from "react";
import {UserContext} from "../UserContext";

export default function Header() {
    const {setUserInfo, userInfo} = useContext(UserContext);

    useEffect(() => {
        fetch('http://localhost:8070/user/profile', {
            credentials: 'include',
        }).then(res => res.json())
            .then(userInfo => {
                setUserInfo(userInfo);
            })
            .catch(err => {
                console.log(err);
            })
    }, []);

    function logout(){
        fetch('http://localhost:8070/user/logout', {
            credentials: 'include',
            method: 'POST',
        });
        setUserInfo(null);
    }

    const email = userInfo?.email;

    return (
        <header>
            <Link to="/" className="logo">
                <img src={logoImage} alt="Spark"/>
            </Link>
            <nav>

                {email && (
                    <>
                        <Link to="/create">
                            <div>New Post</div>
                        </Link>
                        <Link to="/" onClick={logout}>
                            <div>Logout</div>
                        </Link>
                    </>
                )}

                {!email && (
                    <>
                        <Link to="/login">
                            <div>Login</div>
                        </Link>
                        <Link to="/signup">
                            <div>SignUp</div>
                        </Link>
                    </>
                )}

            </nav>
        </header>
    );
}