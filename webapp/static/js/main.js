// Animate Smooth Scroll
$('#view-work').on('click', function(){
	const images = $('#images').position().top;
	console.log(images);
	$('html, body').animate({
		scrollTop: images
	},
	900);
})

// GO TO TOP BUTTON SHOW
// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {scrollFunction()};

function scrollFunction(){
//	const images = $('#images').position().top;
    if (document.body.scrollTop >= 400 ||  document.documentElement.scrollTop >= 400){
        document.getElementById("go-top-btn").style.display = "block";
    }else{
        document.getElementById("go-top-btn").style.display = "none";
    }
}

function goToTop(){
//    document.body.scrollTop = 0;
//    document.documentElement.scrollTop = 0;
    $('html, body').animate({
        scrollTop: 0
    },700);
}
