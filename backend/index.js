const express = require("express");
const mongoose = require("mongoose");
const bodyParser = require("body-parser");
const cors = require("cors");
const dotenv = require("dotenv");
const {notFound, errorHandler} = require("./middleware/errorMiddleware");
const cookieParser = require("cookie-parser");

const app = express();
require("dotenv").config();

/* Configs */
app.use(cors({credentials: true, origin: true}));
app.use(bodyParser.json());
app.use(cookieParser());
// app.use(notFound);
// app.use(errorHandler);

/* Routes */
const userRouter = require("./controllers/userController");
app.use("/user", userRouter);

/* Mongoose Setup */
const PORT = process.env.PORT || 8070;
const URL = process.env.MONGODB_URL;

mongoose.connect(URL, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
});

const connection = mongoose.connection;
connection.once("open", () => {
    console.log("Mongodb Connection Success!");
});

app.listen(PORT, () => {
    console.log(`Server is up and running on port number : ${PORT}`);
});