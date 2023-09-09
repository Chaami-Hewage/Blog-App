const router = require("express").Router();
const asyncHandler = require("express-async-handler");
const User = require("../models/User");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
require("dotenv").config();

const salt = bcrypt.genSaltSync(10);

router.route("/signup").post(
    asyncHandler(async (req, res) => {
        console.log("Received signup request with data:", req.body);
        const {email, password} = req.body;
        try {
            const userData = await User.create({
                email,
                password: bcrypt.hashSync(password, salt),
            });
            res.status(200).json({status: "success", message: "User Registered!", data: userData});
        } catch (err) {
            console.error(err);
            res.status(500).json({status: "error", message: "Error with User Registration"});
        }
    })
);


router.route("/login").post(
    asyncHandler(async (req, res) => {
        try {
            const {email, password} = req.body;

            const userData = await User.findOne({email});

            if (userData && (await bcrypt.compare(password, userData.password))) {
                jwt.sign({email, id:userData._id}, process.env.JWT_SECRET, {}, (err, token) => {
                    if (err) {
                        console.error(err);
                        res.status(500).json({status: "error", message: "Error with User Login"});
                    } else {
                        res.cookie("token", token).json({
                            id:userData._id,
                            email,
                        });
                    }
                });
            } else {
                res.status(401).json({status: "error", message: "Invalid credentials"});
            }

        } catch (err) {
            console.error(err);
            res.status(500).json({status: "error", message: "Error with User Login"});
        }
    })
);

router.route("/profile").get(
    asyncHandler(async (req, res) => {
        try {
            const {token} = req.cookies;
                jwt.verify(token, process.env.JWT_SECRET, {},  (err, info) => {
                    if (err) {
                        console.error(err);
                        res.status(401).json({status: "error", message: "Unauthorized"});
                    } else {
                        res.json(info);
                        res.status(200).json({status: "success", message: "User Profile", data: user});
                    }
                });
        } catch (err) {
            console.error(err);
            res.status(500).json({status: "error", message: "Error with User Profile"});
        }
    })
);

router.route("/logout").post(
    asyncHandler(async (req, res) => {
        try {
            res.clearCookie("token").json({status: "success", message: "User Logged out!"});
        } catch (err) {
            console.error(err);
            res.status(500).json({status: "error", message: "Error with User Logout"});
        }
    })
);

module.exports = router;
