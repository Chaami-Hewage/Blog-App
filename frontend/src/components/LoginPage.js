import React, { useContext, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { UserContext } from '../UserContext';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [redirect, setRedirect] = useState(false);
    const { setUserInfo } = useContext(UserContext);

    async function login(event) {
        event.preventDefault();
        const response = await fetch('http://localhost:8070/user/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
            credentials: 'include',
        });
        if (response.ok) {
            response.json().then((data) => {
                setUserInfo(data);
                setRedirect(true);
            });
        } else {
            alert('Login failed');
        }
    }

    if (redirect) {
        return <Navigate to={'/'} />;
    }

    return (
        <div className="d-flex justify-content-center align-items-center">
            <form className="login text-center" onSubmit={login}>
                <h1>Login</h1>

                <div className="form-outline mb-4">
                    <input
                        type="email"
                        placeholder="Email address"
                        className="form-control"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                    />
                </div>

                <div className="form-outline mb-4">
                    <input
                        type="password"
                        placeholder="Password"
                        className="form-control"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                    />
                </div>

                <button type="submit" className="btn btn-custom-primary btn-block mb-4">
                    Login
                </button>
            </form>
        </div>
    );
}
