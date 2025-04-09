import React from 'react';
import HomePage from './pages/HomePage.js';
import CodePage from './pages/CodePage.js';
import SettingsProvider from "./components/SettingsProvider.js"
import SettingsPage from './pages/SettingsPage.js';
import {BrowserRouter, HashRouter, Routes, Route} from "react-router-dom"

const App = () => {
    return (
        <SettingsProvider>
          <HashRouter>
            <Routes>
              <Route index element={<HomePage/>}/>
              <Route path="CodePage" element={<CodePage/>}/>
              <Route path="Settings" element={<SettingsPage/>}/>
            </Routes>
        </HashRouter>
        </SettingsProvider>
      );
};

export default App;