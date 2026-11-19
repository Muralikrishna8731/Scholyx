
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Scholarships from "./pages/Scholarships";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/scholarships" element={<Scholarships />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
