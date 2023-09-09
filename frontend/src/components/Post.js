export default function Post() {
    return(
        <div className="post">
            <div className="image">
                <img src="https://miro.medium.com/v2/resize:fit:828/format:webp/1*aTEuYNSjEvvxfcl5lT7txA.png"/>
            </div>
            <div className="text">
                <h2>Decoding HTTP Status Codes</h2>
                <p className="info">
                    <a href="" className="auther">Gevin Nanayakkara</a>
                    <time>2023-08-12 00:00</time>
                </p>
                <p className="summary">
                    As an everyday Internet user, you’ve likely encountered those dreaded error pages displaying a
                    “Page Not Found” message. While these HTTP status code errors can be frustrating, they are
                    essential communication tools between web browsers and servers. Whether it’s the familiar 404
                    error or the lesser-known 304 response, these codes convey crucial information about the success
                    or failure of your web requests.
                </p>
            </div>
        </div>
    );
}