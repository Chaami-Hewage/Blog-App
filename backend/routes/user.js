const router = require ("express").Router();
const User = require ("../models/User");

router.route("/signup").post(async (req, res) => {
    try{
        const { email, password } = req.body;

        const userData = await User.create({
            email,
            password
        });

        await userData.save();
        res.status(200).json({ status: "success", message: "User Registered!" });
    } catch (err) {
        console.log(err);
        res.status(500).json({ status: "error", message: "Error with User Registration " });
    }
});

router.route("/login").post(async (req, res) => {
    try{
        const user = await User.findOne({
            email: req.body.email,
            password: req.body.password
        });
        res.status(200).json({ status: "success", message: "User Loged in!" });

    } catch (err) {
        console.log(err);
        res.status(500).json({ status: "error", message: "Error with User Login " });
    }
});

module.exports = router;