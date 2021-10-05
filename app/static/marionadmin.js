$(document).ready(function() {

  setSpeakerTo($(".speaker").eq(0).attr("id"), $(".speaker").eq(0).attr("speakerid"));

  window.marion = true;
  $("body").on("click", "#burger", function(e) {
    $("body").addClass("menuopen");
    e.preventDefault();
  });

  $("#speakers").on("click", ".archive", function(e) {
    //  e.preventDefault();
    e.stopPropagation();
    e.preventDefault();
    var userid = $(this).parent().attr("id");
    $(this).closest(".speaker").slideUp();
    //  $(this).closest(".speaker").hide();
    $("#messages").html("");
    $.ajax({
      type: "GET",
      dataType: 'html',
      url: "/archiveuser?id=" + userid,
      success: function(data) {
        //$("#speakers").html("");
        //updateSpeakers(window.talker);
      }
    });
  });

  $("#speakers").on("click", ".speaker", function(e) {

    $("#messages").html("");

    e.preventDefault();
    var chatID = $(this).attr("id");
    var speakerID = $(this).attr("speakerid");
    setSpeakerTo(chatID, speakerID);
  });

  setInterval(function() {
    updateSpeakers(window.talker);
  }, 10000);

});

function postLoadSpeakers() {
  var newDOM = $("#preload").children();
  //console.log($("#speakers").children().html().length);
  //console.log($("#preload").children().html().length);

  if ($("#speakers").children().html() === $("#preload").children().html()) {
    //if ($("#speakers").children()[0] === $("#preload").children()[0]) {
    //console.log("son iguales");

  } else {
    //if ($("#speakers").children().html().length!== $("#preload").children().html().length) {
    console.log("son speakers diferentes");
    if (newDOM.html().includes('class="notseen"')) {
      //window.audioElement.play();
    }
    $("#speakers").html($("#preload").html());
  }
  var newM = 0;
  $("#speakers .notseen").each(function() {
    newM += parseInt($(this).text());
  });

  notifySpecific(newM);

}

function updateSpeakers(speaker = false) {

  if (speaker) {
    $("#preload").load("/speakers?speaker=" + speaker, function() {
      postLoadSpeakers();
    });
  } else {
    $("#preload").load("/speakers", function() {
      postLoadSpeakers();
    });
  }
}

function setSpeakerTo(chatID, speakerID) {
  $(".speaker").removeClass("active");
  $("#speakers #" + chatID).addClass("active");
  socket.emit('imconnected');
  window.talker = speakerID;
  $("#to").attr("value", speakerID);

  window.talker = chatID;
  //setSpeakerTo(chatID);

  $("#messagebox").val("");

  $("#to").attr("value", window.talker);

  $(this).addClass("active");
  $.ajax({
    type: "POST",
    dataType: 'html',
    url: "/updatechatid",
    data: {
      chatid: chatID
    },
    success: function(data) {
      console.log("speaker switch ok!");

      //updateMessages(true, true);

      socket.emit('browser_ready', {
        data: {
          "chatid": chatID,
          'speakerid': speakerID
        }
      });

      $(".speaker#" + chatID + " .notseen").hide();
      $("body").removeClass("menuopen");
      //$("#messages").html(data);

    },

  });

}
