import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import RouteDetail from "./pages/RouteDetail";
import PublishRoute from "./pages/PublishRoute";
import Profile from "./pages/Profile";

export default function App() {
  return (
    <>
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/routes/:id" element={<RouteDetail />} />
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/routes/:id" element={<RouteDetail />} />
          <Route path="/publish" element={<PublishRoute />} />
          <Route path="/users/:username" element={<Profile />} />
          <Route path="/routes/:id/edit" element={<PublishRoute />} />  
        </Routes>
      </main>
    </>
  );
}