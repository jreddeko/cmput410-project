/**
 * Javascript used in postwall.html
 */
$(document).ready(function (){
    $(".post_buttons").click(function(e) {
        e.preventDefault();
        // reactivate the tinymce with the contents inside
        var currentdbId = $(this).attr("id").split("-")[1];
                             
        if($(this).text().trim() == "Edit")
        {
            if($(".edit_enabled").length >  0)
             {
                 var confirmDialog = $("<div id='confirmation' class='dialog'><p>Please save your other post in editting process before editting another post.</o></div>");
                 $("body").append(confirmDialog);
                 $("#confirmation").dialog({
                   modal: false,
                   width: 300,
                   height: 'auto',
                   buttons: {
                        "Ok": function() {
                            $(this).dialog("close");
                        }
                   }
                   
                });
             }
             else
             {
                text2form(currentdbId);
             
                $("#edit_cancel").click(function(e) {
                     e.preventDefault();
                     $("#post-"+currentdbId).css("display", "block");
                     $("#edit_post-"+currentdbId).empty().remove();
                });
             }
             
        }
        else if($(this).text().trim() == "Delete")
        {
            deletePost(userid, currentdbId)
        }
    });
                  
});

/**
 *
 */
function deletePost(userid, dbId)
{
    var dialogBox = $("<div id='deleteMessage' class='dialog'><p>Are you sure you want to delete this post?</p></div>");
    $("#post-"+dbId).append(dialogBox);
    $("#deleteMessage").dialog({
       modal: true,
       width: 300,
       height: 'auto',
       buttons: {
           "Delete": function() {
               $(this).dialog("close");
               
               // PUT and DELETE type is not supported by firefox
               $.ajax({
                  url: "http://"+window.location.host+"/author/"+userid+"/posts/"+dbId+"/",
                  type: "POST",
                  data: {"method": "delete"},
                  success: function(data) {
                      confirmationDialog(data);
                  },
                  error: function(jqXHR, textStatus, errorThrown) {
                      console.log(jqXHR);
                      console.log(textStatus);
                      console.log(errorThrown);
                  }
                  
                });
           },
           "Cancel" : function() {
                $(this).dialog("close");
                $(this).dialog("destroy");
           }
       }
       
    });
}

function confirmationDialog(message)
{
    var confirmDialog = $("<div id='confirmation' class='dialog'>"+message+"</div>");
    $("body").append(confirmDialog);
    $("#confirmation").dialog({
           modal: false,
           width: 300,
           height: 'auto',
           buttons: {
               "Ok": function() {
                    $(this).dialog("close");
                               window.location.replace("http://"+window.location.host+"/wall");
                }
           }
           
    });
}

function text2form(currentdbId)
{
        // get currently displayed contents of the post
        var headerContent = $("#post-"+currentdbId+" h2").first().text();
        var sourceContent = $("#post_source-"+currentdbId).find("span").first().text();
        var originContent = $("#post_origin-"+currentdbId).find("span").first().text();
        var categoryContent = $("#post_category-"+currentdbId).find("span").first().text();
        var description = $("#post_description-"+currentdbId).find("span").first().text();
        var bodyContent = '';
        $("#post_content-"+currentdbId).children().each(function() {
            if(this.tagName != "h2")
            {
                bodyContent += $(this).html();
            }
        });
        var permissionValue = $("#post_permission-"+currentdbId).val();
        
        createForm(currentdbId);
    
    $("#edit_post_content-"+currentdbId).ready(function() {
         tinymce.init({
              mode: "exact",
              elements: "edit_post_content-"+currentdbId,
              width: '90%',
              plugins: [
                        "advlist autolink lists link image charmap preview anchor",
                        "searchreplace visualblocks code fullscreen",
                        "insertdatetime media table contextmenu paste"
                        ],
              toolbar: "insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image",
              setup : function(ed) {
                ed.on("init", function(e) {
                    ed.setContent(bodyContent);
                });
              },
        });
     });

    $("#post-"+currentdbId).css("display", "none");
    
    $("#spec_author_div-"+currentdbId).hide();
    
        $("#post_title-"+currentdbId).val(headerContent);
        $("#edit_post_source-"+currentdbId).val(sourceContent);
        $("#edit_post_origin-"+currentdbId).val(originContent);
        // categories has giant gaps! need to trim all!
        var processedCategories = categoryContent.split(",");
        var newCategoryString = processedCategories[0].trim();
    
        for (var i=1; i < processedCategories.length; i++)
        {
            newCategoryString += ", "+processedCategories[i].trim();
        }
        $("#edit_post_category-"+currentdbId).val(newCategoryString);

        $('select#post_permissions-'+currentdbId).children().each(function() {
            var currentVal = $(this).attr("value");
            if(currentVal.trim() == permissionValue.trim())
            {
                $("#edit_post_permission-"+currentdbId).val(3)
            }
            else
            {
                if($(this).attr("selected") ==  "selected")
                {
                    $(this).removeAttr("selected");
                }
            }
        });
        
        $("#edit_post_description-"+currentdbId).val(description);
}

function createForm(id)
{
    var form = $('<div id="edit_post-'+id+'" class="edit_enabled"class="well">'+
                    '<h3>Edit Post</h3>'+
                    '<form class="form-horizontal" action="" method="POST">'+
                        '<div class="form-group">'+
                            '<label for="post_permissions" class="col-sm-3">Permissions:</label>'+
                            '<div class="col-sm-9">'+
                                '<select id="edit_post_permissions-'+id+'" name="post_permissions-'+id+'" class="col-sm-9 form-control" style="width: 90%;">'+
                                    '<option value="private" selected="selected">Private</option>'+
                                        '<option value="spec_author">Specify</option>'+
                                        '<option value="friends">Friends</option>'+
                                        '<option value="friendsoffriends">Friends of my friends</option>'+
                                        '<option value="local">Friends within my host</option>'+
                                        '<option value="public">Public</option>'+
                                    '</select>'+
                                '</div>'+
                            '</div>'+
                             '<div id="spec_author_div-'+id+'" class="form-group">'+
                                    '<label for="spec_author_input-'+id+'" class="col-sm-3"> Author\'s username:</label>'+
                                    '<div class="col-sm-9">'+
                                        '<input id="spec_author_input-'+id+'" name="spec_author_input-'+id+'" style="width: 90%;" placeholder="Please input the author\'s username."/>'+
                                    '</div>'+
                                '</div>'+
                            '<div class="form-group">'+
                                '<label for="post_title-'+id+'" class="col-sm-3">Title: </label>'+
                                '<div class="col-sm-9">'+
                                    '<input type="text" id="post_title-'+id+'" name="post_title-'+id+'" style="width: 90%;" placeholder="Title of the post"/>'+
                                '</div>'+
                            '</div>'+
                 '<div class="form-group">'+
                    '<label for="edit_post_source-'+id+'" class="col-sm-3">Source of the Post: </label>'+
                    '<div class="col-sm-9">'+
                        '<input type="text" id="edit_post_source-'+id+'" name="post_source-'+id+'" style="width: 90%;" placeholder="Source URI of the post"/>'+
                    '</div>'+
                 '</div>'+
                 '<div class="form-group">'+
                    '<label for="edit_post_origin-'+id+'" class="col-sm-3">Origin of the Post: </label>'+
                    '<div class="col-sm-9">'+
                        '<input type="text" id="edit_post_origin-'+id+'" name="post_origin-'+id+'" style="width: 90%;" placeholder="Origin of the post (URI)"/>'+
                    '</div>'+
                 '</div>'+
                 '<div class="form-group">'+
                    '<label for="edit_post_category-'+id+'" class="col-sm-3">Category of the Post: </label>'+
                    '<div class="col-sm-9">'+
                        '<input type="text" id="edit_post_category-'+id+'" name="post_category-'+id+'" style="width: 90%;" placeholder="(e.g. Medical, Health)"/>'+
                    '</div>'+
                 '</div>'+
                            '<div class="form-group">'+
                                '<label for="edit_post_description-'+id+'" class="col-sm-3">Post Description:</label>'+
                                '<div class="col-sm-9">'+
                                  '<input id="edit_post_description-'+id+'" name="post_description-'+id+'" style="width: 90%;" placeholder="Description of the post"/>'+
                                '</div>'+
                            '</div>'+
                            '<div class="form-group">'+
                                '<label for="edit_post_content-'+id+'" class="col-sm-3">Post Content:</label>'+
                                '<div class="col-sm-9">'+
                                  '<textarea id="edit_post_content-'+id+'" class="mceEditor" name="post_content-'+id+'" style="width: 90%;"></textarea>'+
                                '</div>'+
                            '</div>'+
                            '<div class="form-group">'+
                                '<label class="col-sm-3"></label>'+
                                '<div class="col-sm-9">'+
                                    '<button class="btn btn-primary btn-md" name="edit" type="submit" width: 10%;">Edit</button>'+
                                    '<button id="edit_cancel" class="btn btn-default btn-md" width: 10%;">Cancel</button>'+
                                '</div>'+
                            '</div>'+
                        '</form>'+
                    '</div>');
    $(form).appendTo($("#post_wall"));
}