var hoje = new Date();
var dia = (hoje.getDate() < 10 ? "0" + hoje.getDate() : hoje.getDate());
var mes = hoje.getMonth()+1;
var mesTemp = (mes < 10 ? "0" + mes : mes); 
var ano = "2024"

window.onload = function(){
    GetDay();
    // GetDayTides("11",Meses[0]);
};

function GetDay(){    
    var today = new Date();
    var day = (today.getDate() < 10 ? "0" + today.getDate() : today.getDate()); // retorna o dia do mês 1 - 31
    var realMonth = today.getMonth() + 1; // retorna 0 para Janeiro e 11 para Dezembro por isso somar mais 1
    var month = (realMonth < 10 ? "0" + realMonth : realMonth); 
    var year = today.getFullYear();
    var realDate = day + "/" + month + "/" + year;
    document.getElementById("Today").innerText += "" + realDate + "";
    GetDayTides(day,Meses[today.getMonth()]); // aqui que chamo a função de plotar os dados
    callApi();
}

function GetDayTides(day,month) {
    var weekDay = month[day].DIA;
    // var moonPhase = month[day].LUA;
    var FirstTide =  month[day]["MARE1"]["Horário"];
    var FirstTideHeight = month[day]["MARE1"]["Altura"];
    var SecondTide =  month[day]["MARE2"]["Horário"];
    var SecondTideHeight = month[day]["MARE2"]["Altura"];
    var ThirdTide =  month[day]["MARE3"]["Horário"];
    var ThirdTideHeight = month[day]["MARE3"]["Altura"];


    if (month[day]["MARE4"]) {
        let elemento = document.getElementById("t4");  
        elemento.classList.remove("invisible");
        elemento.classList.add("visible");
        // elemento.style.visibility="visible";

        var FourthTide =  month[day]["MARE4"]["Horário"];
        var FourthTideHeight = month[day]["MARE4"]["Altura"];
        document.getElementById("tideType4").innerText =  (FourthTideHeight > ThirdTideHeight) ? "Maré Alta" : "Maré Baixa";
        document.getElementById("FourthTide").innerText = FourthTide[0] + "" + FourthTide[1] + "h" + FourthTide[2] + "" + FourthTide[3] + "m";
        document.getElementById("FourthTideHeight").innerText = FourthTideHeight + " m";
    }else{ // Remove a quarta maré se ela não existir
        let elemento = document.getElementById("t4");  
        // elemento.style.visibility="hidden";
        // elemento.parentElement.remove(elemento);
        elemento.classList.remove("visible");
        elemento.classList.add("invisible");
        
    }


    

    // Veirifica as Marés se são de baixa ou de alta
    document.getElementById("tideType1").innerText =  (FirstTideHeight > SecondTideHeight) ? "Maré Alta" : "Maré Baixa";
    document.getElementById("tideType2").innerText =  (SecondTideHeight > FirstTideHeight) ? "Maré Alta" : "Maré Baixa";
    document.getElementById("tideType3").innerText =  (ThirdTideHeight > SecondTideHeight) ? "Maré Alta" : "Maré Baixa";
   


    document.getElementById("weekDay").innerText = "(" + weekDay + ")";
    // document.getElementById("moon").innerText = "LUA " + moonPhase;
    // document.getElementById("moonIcon").src = "./icones/"+moonPhase+".png";
    document.getElementById("FirstTide").innerText = FirstTide[0] + "" + FirstTide[1] + "h" + FirstTide[2] + "" + FirstTide[3] + "m";
    document.getElementById("FirstTideHeight").innerText = FirstTideHeight + " m";
    document.getElementById("SecondTide").innerText = SecondTide[0] + "" + SecondTide[1] + "h" + SecondTide[2] + "" + SecondTide[3] + "m";
    document.getElementById("SecondTideHeight").innerText = SecondTideHeight + " m";
    document.getElementById("ThirdTide").innerText = ThirdTide[0] + "" + ThirdTide[1] + "h" + ThirdTide[2] + "" + ThirdTide[3] + "m";
    document.getElementById("ThirdTideHeight").innerText = ThirdTideHeight + " m";
}

function NextDay() {
    var mesReal = mes-1;
    dia < Object.keys(Meses[mesReal]).length ? dia++ : dia="1"

    if (dia < 10) {
        dia = "0" + dia; 
    }

    var DataReal = dia + "/" + mesTemp + "/" + ano;
    document.getElementById("Today").innerText = "" + DataReal + "";
    GetDayTides(dia,Meses[mesReal]);
}

function PreviousDay() {
    var mesReal = mes-1;
    dia > 1 ? dia-- : dia=Object.keys(Meses[mesReal]).length;
    if (dia < 10) {
        dia = "0" + dia; 
    }
    var DataReal = dia + "/" + mesTemp + "/" + ano;
    document.getElementById("Today").innerText = "" + DataReal + "";
    GetDayTides(dia,Meses[mesReal]);
}