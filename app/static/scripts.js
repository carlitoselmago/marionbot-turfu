window.loaded = false;
window.user = 0;
window.messagaesPosted = 0;





var socket = io();

$(document).ready(function() {
  window.originalTitle = document.title;
  window.posted = false;
  window.marion = false;
  window.unseen = 0;
  window.favicon = new Favico({
    animation: 'popFade'
  });
  var icon = document.getElementById('favicon');
  window.favicon.image(icon);

  if (($(".login").length) && (ififramedlimited())){
    console.log("IFRAMED LIMITED",ififramedlimited());
    $(".secondaryinfo").html('<a href="https://turfu-festival.ddns.net/" target="_blank" class="btn iframedstart">Converser avec <span class="mname">Marion</span></a>');
  }


  if ($("#burger").length) {
    window.marion = true;
  }
  window.talker = $("#messages").attr("to");
  window.connected = true;

  //chat 100vh mobile hack
  mobile100vh();
  createAlertSound();

  $(window).resize(function() {
    mobile100vh();
  });

  //login
  $("#signinbutton").click(function(e) {
    e.preventDefault();

    $("#signinform").slideDown();
  });

  $("#messagebox").keyup(function() {
    $(".messageinputwrap").addClass("typing");
  });

  $(".send").click(function() {
    $("#inputuser").submit();
  });

  $("body").on("click", ".flashes li", function() {
    $(this).remove();
  });

  $(window).focus(function() {
    clearNotify();
  });

  if ($(".messageinputwrap").length) {
    var tipping = '<div id="tipping" class="message"><div class="bubble"><img src="static/dots.gif" alt="tipping" /></div></div>';
    if ($("#tipping").length == 0) {
      $("#messages").append(tipping);
    }
  }

  //////////SOCKET IO///////////////////////////////////////////////////////////

  socket.on('connect', () => {
    console.log("connect ");
  });

  if ($("#mainchat").length) {
    socket.emit('imconnected');
  }

  socket.on('welcome', function(data) {
    console.log("got welcome!");
    if (window.connected == false) {
      showError("Connexion au serveur rétablie", 2);
    } else {
      console.log("**************conected");
    }
    window.connected = true;
    window.user = data["userid"];
    socket.emit('browser_ready', {
      data: {
        "userid": window.user
      }
    });
  });

  socket.on("heartbeat", function() {
    setTimeout(function() {
      socket.emit("heartbeat")
    }, 2000);
  })


  socket.on('initmessages', function(data) {
    console.log("INIT MESSAGES!");
    handleMessagesAPI(data, true, true);
  });

  socket.on('newmessages', function(data) {
    console.log("new messages");
    handleMessagesAPI(data, true, false);
  });


  socket.on('connect_error', function() {
    showError("Déconnexion du serveur", 1);
    window.connected = false;
  });

  socket.on('boterror', function() {
    showError("Marion n'est pas disponible pour le moment", 1);
    window.connected = false;
  });


  /////////END SOCKET IO////////////////////////////////////////////////////////

  $("#inputuser").submit(function(e) {
    $("#tipping").removeClass("hide");
    var text = $("#messagebox").val();
    $("#messagebox").val("");

    e.preventDefault(); // avoid to execute the actual submit of the form.
    var last = $(".contmsg:last").attr("date");
    data = {
      "message": text,
      "last": last
    };
    setTimeout(function() {
      scrollDown();
    }, 300);
    window.messagaesPosted++;
    socket.emit("post", data);
    if ($("#mainchat").attr("access") == "0" && window.messagaesPosted == 1) {
      setTimeout(function() {
        location.reload();
      }, 6000);
    }
  });


});


function scrollDown() {
  setTimeout(function() {
    $('#messages').scrollTop($('#messages')[0].scrollHeight);
  }, 100);

}

function checkMessagesSeen() {
  var markasseen = [];
  $(".message").each(function(index) {
    if ($(this).attr('seen') == "0") {
      if ($(this).is(':visible')) {
        markasseen.push(parseInt($(this).attr("id")));
      }
    }
  });
  var url = "/markasseen"
  $.ajax({
    method: "POST",
    url: url,
    data: {
      "seen": markasseen
    },
    success: function(data) {
      console.log("marked as seen", markasseen);
    }
  });
}



//draganddrop

$(document).on('click', '#upload-btn', function(e) {
  //  $(".dropzone").show();
  $(".dropzone").trigger("click");
});

$(document).on('dragenter', '#messages', function(e) {
  $(".dropzone").show();
  $('#messages').hide();
  $("#drop").addClass("hover");
});

$(document).on('dragleave', '#myDropzone', function(e) {
  $('#messages').show();
  $(".dropzone").hide();
  $("#drop").removeClass("hover");
});

function handleMessagesAPI(data, scrolldownatend = false, allmessages = true) {
  $("#tipping").addClass("hide");

  var dom = $('<div></div>').html(data);

  if (!allmessages) {

    var newmessages = dom;

    $(".message", newmessages).each(function(index) {
      if ($("#messages .contmsg#" + $(this).attr("id")).length == 0) {
        $("#messages").append($(this));
      }
    });

  } else {
    console.log("All messages");
    document.getElementById('messages').innerHTML = data;
  }
  //end new memory way

  if (window.loaded) {
    if (!window.marion) {
      if (data.length > 0) {

        //only if marion messages
        var newMm = 0;

        $(dom).find(".contmsg").each(function() {
          if (!$(this).hasClass("me")) {
            newMm++;
          }
        });

        //notify($(dom).find(".message").length);
        notify(newMm);
        //window.audioElement.play();
      }
    }
  }
  if (!window.loaded) {

    if ($("#messages img").length) {
      $("#messages img").on("load", function() {
        if (data.length > 0) {
          scrollDown();
        }

      });
    } else {
      if (data.length > 0) {
        scrollDown();
      }
    }
  }
  if (scrolldownatend) {
    if (data.length > 0) {
      scrollDown();
    }
  }
  //}
  window.loaded = true;
}

function createAlertSound() {
  window.audioElement = document.createElement('audio');
  window.audioElement.setAttribute('src', 'static/cuak.mp3');
}

function mobile100vh() {
  if ($("#messages").length) {
    var extra = 109;

    if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
      $(".heightfix,.dropzone").height(window.innerHeight - extra);
    }
  }
}

function showError(text, mode = 0) {
  //modes: 0 add, 1 add if not already shown, 2 not error but info (positive)
  if ($(".flashes").length == 0) {
    $("body").append('<ul class="flashes"></ul>');
  }
  if (mode == 1) {

    if ($('.flashes:contains("' + text + '")').length == 0) {
      $(".flashes").append('<li>' + text + '</li>');
    }
  } else {
    if (mode == 2) {

      $(".flashes").html('<li class="success">' + text + '</li>');
      setTimeout(function() {
        $(".flashes .success").fadeOut("slow");
      }, 3000);

    } else {
      $(".flashes").append('<li>' + text + '</li>');
    }
  }
}


function fileSucces() {
  $('#messages').show();
  $(".dropzone").hide();
  $("#drop").removeClass("hover");
}

function notify(newMessagesNum) {
  //var newTitle = '(' + newMessagesNum + ') ' + window.originalTitle;
  //document.title = newTitle;
  window.unseen += newMessagesNum;
  window.favicon.badge(window.unseen);
}

function notifySpecific(newMessagesNum) {
  //var newTitle = '(' + newMessagesNum + ') ' + window.originalTitle;
  //document.title = newTitle;
  window.favicon.badge(newMessagesNum);
}

function clearNotify() {
  window.unseen = 0;
  window.favicon.reset();
  if (window.marion) {
    var speakerID = $(".speaker.active").attr("id");
    //$(".speaker.active .notseen").remove();

    $.ajax({
      type: "POST",
      dataType: 'html',
      url: "/updatechatid",
      data: {
        chatid: speakerID
      }
    });

  }
}

function ififramedlimited() {

  if (window.location !== window.parent.location) {
    //iframed
    var is_chrome = /chrome/i.test( navigator.userAgent );
    //console.log("chrome",is_chrome);
    if(is_chrome){
      return true;
    }
  }
  return false;
}
