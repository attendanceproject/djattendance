// Import TinyMCE
// see https://github.com/fyrkant/simple-tinymce-webpack
// see https://www.tinymce.com/docs/advanced/usage-with-module-loaders/#webpackfile-loader
import tinymce from "tinymce/tinymce";

// A theme is also required
import "tinymce/themes/modern";

// Any plugins you want to use has to be imported
//"advlist autolink autosave link image lists charmap print preview hr anchor pagebreak",
import "tinymce/plugins/advlist";
import "tinymce/plugins/autolink";
import "tinymce/plugins/autosave";
import "tinymce/plugins/link";
import "tinymce/plugins/image";
import "tinymce/plugins/lists";
import "tinymce/plugins/charmap";
import "tinymce/plugins/print";
import "tinymce/plugins/preview";
import "tinymce/plugins/hr";
import "tinymce/plugins/anchor";
import "tinymce/plugins/pagebreak";

//"searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking",
import "tinymce/plugins/searchreplace";
import "tinymce/plugins/wordcount";
import "tinymce/plugins/visualblocks";
import "tinymce/plugins/visualchars";
import "tinymce/plugins/code";
import "tinymce/plugins/fullscreen";
import "tinymce/plugins/insertdatetime";
import "tinymce/plugins/media";
import "tinymce/plugins/nonbreaking";

//"table contextmenu directionality emoticons template textcolor paste fullpage textcolor colorpicker textpattern"
import "tinymce/plugins/table";
import "tinymce/plugins/contextmenu";
import "tinymce/plugins/directionality";
import "tinymce/plugins/emoticons";
import "tinymce/plugins/template";
import "tinymce/plugins/textcolor";
import "tinymce/plugins/paste";
//import "tinymce/plugins/fullpage";
import "tinymce/plugins/colorpicker";
import "tinymce/plugins/textpattern";
import "tinymce/plugins/autoresize"


let pluginStr = "advlist autolink autosave link image lists charmap print preview hr anchor pagebreak " +
    "searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking " +
    "table contextmenu directionality emoticons template textcolor paste textcolor colorpicker textpattern autoresize";

let pluginList = pluginStr.split(" ");

require.context(
  "url-loader?name=[path][name].[ext]&context=node_modules/tinymce!tinymce/skins",
  true,
  /.*/
);

tinymce.init({
  selector: "textarea",
  plugins: pluginStr,

  //autoresize
  autoresize_max_height: 500,
  autoresize_on_init: false,

  //image uploader/picker
  /****************/
  // There are two ways of using images through the following configuration
  // 1. the img src is raw data (which is duplicated in export_to_json) - this is done through the file picker UI
  // 2. the ims src is a url to an uploaded image - this is done through the file upload dialogue (drag & drop)
  /****************/
 // enable title field in the Image dialog
  image_title: true,

  // Method 2
  // enable automatic uploads of images represented by blob or data URIs
  automatic_uploads: false,
  // allows you to pass along credentials like cookies etc cross domain to the configured images_upload_url
  images_upload_credentials: true,  //TODO: not working with csrf
  // URL of our upload handler (for more details check: https://www.tinymce.com/docs/configure/file-image-upload/#images_upload_url)
  images_upload_url: "/gospel_trips/upload/",


  // Method 1
  // here we add custom filepicker only to Image dialog
  file_picker_types: "image",
  // and here's our custom image picker
  file_picker_callback: function(cb, value, meta) {
    var input = document.createElement("input");
    input.setAttribute("type", "file");
    input.setAttribute("accept", "image/*");

    // Note: In modern browsers input[type="file"] is functional without
    // even adding it to the DOM, but that might not be the case in some older
    // or quirky browsers like IE, so you might want to add it to the DOM
    // just in case, and visually hide it. And do not forget do remove it
    // once you do not need it anymore.

    input.onchange = function() {
      var file = this.files[0];

      var reader = new FileReader();
      // reader.readAsDataURL(file);
      reader.onload = function () {
        // Note: Now we need to register the blob in TinyMCEs image blob
        // registry. In the next release this part hopefully won't be
        // necessary, as we are looking to handle it internally.
        var id = "blobid" + (new Date()).getTime();
        var blobCache =  tinymce.activeEditor.editorUpload.blobCache;
        var base64 = reader.result.split(",")[1];
        var blobInfo = blobCache.create(id, file, base64);
        blobCache.add(blobInfo);

        // call the callback and populate the Title field with the file name
        cb(blobInfo.blobUri(), { title: file.name });
      };
      reader.readAsDataURL(file);
    };

    input.click();
  }
});

// Initialize
tinymce.init({
  selector: ".editor",
  theme: "lightgray",
  inline: true,

});
