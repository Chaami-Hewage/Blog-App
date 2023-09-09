import React from 'react';

export default function LoginPage() {
    return (
        <div className="d-flex justify-content-center align-items-center">
            <form className="login text-center">

                <h1>Login</h1>

                <div className="form-outline mb-4">
                    <input type="email" placeholder="Email address" id="form2Example1" className="form-control" />
                </div>

                <div className="form-outline mb-4">
                    <input type="password" placeholder="Password" id="form2Example2" className="form-control" />
                </div>

                <button type="button" className="btn btn-dark btn-block mb-4">Login</button>

            </form>
        </div>
    );
}
