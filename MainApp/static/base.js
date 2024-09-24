function toggleMenu(){
    menu = document.getElementById("nav_section");
    console.log(menu.style.display);
    // if display is none set it to flex
    if(menu.style.display == "none" || menu.style.display == ""){
        menu.style.display = "flex";
    }else{
        menu.style.display = "none";
    }

}