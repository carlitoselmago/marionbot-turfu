Dropzone.options.myDropzone = {
  init: function() {
    this.on("addedfile", function(file) {
        fileSucces();
      }),
      this.on("sending", function(file, xhr, formData) {
        var chatid = window.talker;
        formData.append("to", chatid);
      }),
      this.on("success", function(file) {
        this.removeAllFiles(true);
        $(".message:last img").load(function(){
            scrollDown();
        });

      }),
      this.on("error", function(error) {
        console.log(error);
        showError("Erreur de chargement de l'image ! format accepté : .jpg, .png ; taille de l'image : 5Mo maximum", 1);
        this.removeAllFiles(true);

      })
  },
  acceptedFiles: ".jpg, .png",
  dictDefaultMessage: '<span class="plusulpload">+</span>',
  dictInvalidFileType: 'Formats acceptés : .jpg, .png'
};
