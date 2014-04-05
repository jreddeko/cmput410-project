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
                   autoOpen: true,
                   modal: false,
                   width: 300,
                   dialogClass: "no-close",
                   open: function() {
                       // the code below is needed to fix the autoscroll problem with jquery UI dialog
                       // It manually resets the position of the dialog
                       var parenttop = $("body").position().top;
                       $(".no-close").css("top",parenttop+200);
                       $("html, body").scrollTop(parenttop);
                   },
                   buttons: {
                        "Ok": function() {
                            $(this).dialog("close");
                            $(this).empty().remove();
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
            deletePost(username, currentdbId)
        }
    });
                  
    $("#public_posts").click(function(e){
        e.preventDefault;
        $.ajax({
              url: "http://"+window.location.host+"/posts/",
              type: "GET",
              success: function(data) {
                  displayJsonData(data);
              },
              error: function(jqXHR, textStatus, errorThrown) {
                  console.log(jqXHR);
                  console.log(textStatus);
                  console.log(errorThrown);
              }
              
          });
    });
                  
});

/**
 * Takes the JSON data returned from the GET requests and
 * displays them in the post wall main page.
 *
 * @param json          JSON data from the AJAX calls
 */
function displayJsonData(json)
{
    var posts = json["posts"];
    
    for(var i=0; i < posts.length; i++)
    {
        // do this by components (b/c need to check for empty data...)
        /*var html = $('<div id="post_wall-'+posts[i]["guid"]+'" class="col-sm-8 blog-main">'+
                     '<div id="post-'+posts[i]["guid"]+'"class="blog-post">'+
                     '<button id="post_delete-'+posts[i]["guid"]+'" type="button" class="btn btn-primary btn-lg post_buttons">'+
                     '<span class="glyphicon glyphicon-trash"></span> Delete'+
                     '</button>'+
                     '<button id="post_edit-'+posts[i]["guid"]+'" type="button" class="btn btn-primary btn-lg post_buttons">'+
                     '<span class="glyphicon glyphicon-pencil"></span> Edit'+
                     '</button>'+
                     '<h2 class="blog-post-title">'+ post +'</h2>'+
                     {% if post.categories %}
                     <div id="post_category-'+posts[i]["guid"]+'">
                     <p class="blog-post-meta">Categories: <span>
                     {% for cat in post.categories %}
                     {% if not forloop.last %}
                     {{ cat }},
                     {% else %}
                     {{ cat }}
                     {% endif %}
                     {% endfor %}
                     </span>
                     </p>
                     </div>
                     {% endif %}
                     {% if post.source %}
                     <div id="post_source-'+posts[i]["guid"]+'">
                     <p class="blog-post-meta" style="margin-bottom:2px;">Source: <span>{{ post.source }}<span></p>
                     </div>
                     {% endif %}
                     {% if post.origin %}
                     <div id="post_origin-'+posts[i]["guid"]+'">
                     <p class="blog-post-meta">Origin: <span>{{ post.origin }}<span></p>
                     </div>
                     {% endif %}
                     {% if post.description %}
                     <div id="post_description-'+posts[i]["guid"]+'">
                     <p class="blog-post-meta">Description of the Post: <span>{{ post.description }}</span></p>
                     </div>
                     {% endif %}
                     <div id="post_content-'+posts[i]["guid"]+'" class="blog_content">
                     {{ post.content | safe }}
                     </div>
                     <div id="post_author_info-'+posts[i]["guid"]+'">
                     <p class="blog-post-meta">Posted on {{post.pubDate}} by <a href="#">{{ post.author.displayname }}</a></p>
                     </div>
                     <!-- hidden div where it will be storing the permissions value from the DB. Needed when editting the post to load previous contents asynchronously -->
                     <input id="post_permission-'+posts[i]["guid"]+'" type="hidden" value="{{ post.visibility }}"/>
                     <div id="post_comment-'+posts[i]["guid"]+'" class="well">
                     <h4> Comments </h4>
                     
                     {% for comment in comments %}
                     {%  if comment.postguid.guid == post.guid %}
                     
                     <div id="post_comment-{{ comment.guid }}" class="post_comments">
                     <p> {{ comment.comment }} </p>
                     <p class="blog-post-meta">Commented by: {{ comment.author.username }}</p>
                     </div>
                     {% endif %}
                     {% endfor %}
                     </div>
                     
                     <div id="post_comment-'+posts[i]["guid"]+'" class="well">
                     <div class="form-group">
                     <form class="form-horizontal" action="/author/{{username}}/posts/'+posts[i]["guid"]+'/comments/" method="post">{% csrf_token %}
                     <label for="id_comment" class="col-sm-3">Your comment:</label>
                     {{ comment_form.comment }}
                     <input type="submit" name="comment_submit_form" class="btn btn-primary" value="Submit" />
                     
                     </form>
                     </div>
                     </div><!-- end of comments -->
                     
                     </div><!-- end of post -->
                     
                     </div><!-- /.blog-main -->')*/
    }
}

/**
 *  This javascript method is called when the delete button is triggered
 *  on top of the post div.  It will call an jQuery UI Dialog to confirm
 *  the deletion with the user and upon user's confirmation, it will delete
 *  the post.  The database record is deleted by an ajax call to the
 *  webservices host/authors/username/posts/post_id
 *
 *  @param username         the username stored in the session
 *  @param dbId             the database ID of the post being triggered for delete
 */
function deletePost(username, dbId)
{
    var dialogBox = $("<div id='deleteMessage' class='dialog'><p>Are you sure you want to delete this post?</p></div>");
    $("#post-"+dbId).append(dialogBox);
    $("#deleteMessage").dialog({
       autoOpen: true,
       modal: true,
       dialogClass: "no-close",
       width: 300,
       open: function() {
            // the code below is needed to fix the autoscroll problem with jquery UI dialog
            // It manually resets the position of the dialog
           var parenttop = $("#post_wall-"+dbId).position().top;
           $(".no-close").css("top",parenttop+200);
           $("html, body").scrollTop(parenttop);
       },
       buttons: {
           "Delete": function() {
               $(this).dialog("close");
               
               // PUT and DELETE type is not supported by firefox
               $.ajax({
                  url: "http://"+window.location.host+"/author/"+username+"/posts/"+dbId+"/",
                  type: "POST",
                  data: {"method": "delete"},
                  success: function(data) {
                      $(this).empty().remove();
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
                $(this).empty().remove();
           }
       }
       
    });
}

/**
 * This javascript function creates a jQuery UI dialog to notify the
 * the user that the post has been deleted from the database.  This
 * function is triggered from above method when the user triggers
 * the "Delete" button in the dialog.
 *
 * @param message   the mesage that will be shown to the user.
 */
function confirmationDialog(message)
{
    var confirmDialog = $("<div id='confirmation' class='dialog'>"+message+"</div>");
    $("body").append(confirmDialog);
    $("#confirmation").dialog({
           modal: false,
           width: 300,
           height: 'auto',
           dialogClass: "no-close",
           open: function() {
           // the code below is needed to fix the autoscroll problem with jquery UI dialog
           // It manually resets the position of the dialog
                var parenttop = $("body").position().top;
                $(".no-close").css("top",parenttop+200);
                $("html, body").scrollTop(parenttop);
           },
           buttons: {
               "Ok": function() {
                    $(this).dialog("close");
                               window.location.replace("http://"+window.location.host+"/wall");
                }
           }
           
    });
}

/**
 *  This function is used to create form and load the existing post data
 *  to be editted.  It is triggered by the Edit button on top of the post
 *  div.
 *  
 *  @param currentdbId  the database ID associated with the currently being editted post
 */
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
    
    // initialize the tinyMCE editor for the newly added textarea and load the content
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

/**
 * This method creates the form needed to edit the post.
 * It is called by the above method to create the form before
 * populating it with exisiting data.
 *
 * @param id    database ID that is associated with the current post
 */
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
    $(form).appendTo($("#post_wall-"+id));
}