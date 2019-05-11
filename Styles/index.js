function compatible(works_min, works_max, tweak_compatibility) {
    let currentiOS = parseFloat(('' + (/CPU.*OS ([0-9_]{1,})|(CPU like).*AppleWebKit.*Mobile/i.exec(navigator.userAgent) || [0,''])[1]).replace('undefined', '3_2').replace('_', '.').replace('_', ''));
    works_min = numerize(works_min);
    works_max = numerize(works_max);
    let el = document.querySelector(".compatibility");
    if(currentiOS < works_min) {
        el.innerHTML = "Your version of iOS is too old for this package. This package works on " + tweak_compatibility + ".";
        el.classList.add("red")
    } else if(currentiOS > works_max) {
        el.innerHTML = "Your version of iOS is too new for this package. This package works on " + tweak_compatibility + ".";
        el.classList.add("red")
    } else if(String(currentiOS) != "NaN") {
        el.innerHTML = "This package works on your device!";
        el.classList.add("green")
    }
}
function numerize(x) {
    return x.substring(0,x.indexOf(".")) + "." + x.substring(x.indexOf(".")+1).replace(".","")
}
function swap(hide, show) {
    for (var i = document.querySelectorAll(hide).length - 1; i >= 0; i--) {
        document.querySelectorAll(hide)[i].style.display = "none";
    }
    for (var i = document.querySelectorAll(show).length - 1; i >= 0; i--) {
        document.querySelectorAll(show)[i].style.display = "block";
    }
    document.querySelector(".nav_btn" + show + "_btn").classList.add("active");
    document.querySelector(".nav_btn" + hide + "_btn").classList.remove("active")
}

function externalize() {
    for (var i = document.querySelectorAll("a").length - 1; i >= 0; i--) {
        document.querySelectorAll("a")[0].setAttribute("target","blank")
    }
}