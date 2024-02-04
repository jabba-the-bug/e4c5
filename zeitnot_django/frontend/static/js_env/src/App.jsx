import React from 'react';
import ReactDOM from 'react-dom';

import IndexPage from './pages/IndexPage';


const Registry =[
    {"id": "#indexPage", "component": IndexPage}
]


const renderApp = () => {
    Registry.forEach((itm) => {
        document.querySelectorAll(itm.id).forEach((elem) => {
            let data = "{}"
            if(elem.getAttribute("react_data")){
                data = elem.getAttribute("react_data")
            }
            ReactDOM.render(<itm.component passed={JSON.parse(data)} />, elem, );
        })
    })
}

renderApp();