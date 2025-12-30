import express from "express"
import cors from "cors"
import cookieParser from "cookie-parser"
import mapRouter from "./routes/map.route.js";

const app = express();


//middlewares
app.use(cors())
app.use(express.json({limit: "16kb"}))
app.use(express.urlencoded({extended: true, limit: "16kb"}))
app.use(cookieParser())

//api declaration
app.use("/api/v1/map",mapRouter)


export {app}