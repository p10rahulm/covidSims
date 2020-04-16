function clickHome() {
    document.getElementById("home").classList.remove("main-inactive");
    document.getElementById("home").classList.add("main-active");
    document.getElementById("about").classList.remove("main-active");
    document.getElementById("about").classList.add("main-inactive");
    document.getElementById("team").classList.remove("main-active");
    document.getElementById("team").classList.add("main-inactive");

    document.getElementById("navbar-home").classList.add("navbar-active");
    document.getElementById("navbar-about").classList.remove("navbar-active");
    document.getElementById("navbar-team").classList.remove("navbar-active");


}

function clickAbout() {
    document.getElementById("home").classList.remove("main-active");
    document.getElementById("home").classList.add("main-inactive");
    document.getElementById("about").classList.remove("main-inactive");
    document.getElementById("about").classList.add("main-active");
    document.getElementById("team").classList.remove("main-active");
    document.getElementById("team").classList.add("main-inactive");

    document.getElementById("navbar-home").classList.remove("navbar-active");
    document.getElementById("navbar-about").classList.add("navbar-active");
    document.getElementById("navbar-team").classList.remove("navbar-active");
}


function clickTeam() {
    document.getElementById("home").classList.remove("main-active");
    document.getElementById("home").classList.add("main-inactive");
    document.getElementById("about").classList.remove("main-active");
    document.getElementById("about").classList.add("main-inactive");
    document.getElementById("team").classList.remove("main-inactive");
    document.getElementById("team").classList.add("main-active");

    document.getElementById("navbar-home").classList.remove("navbar-active");
    document.getElementById("navbar-about").classList.remove("navbar-active");
    document.getElementById("navbar-team").classList.add("navbar-active");
}
