/**
 * Javascript used in postwall.html
 */
$(document).ready(function (){
    postButtonClickEvent();
    
    // bind click event to the "All" in the right side of the page
    $("#all_posts").click(function(e) {
        e.preventDefault();
        $.ajax({
            url: "http://"+window.location.host+"/author/posts/",
            type: "GET",
            success: function(data) {
                displayJsonData(data["posts"]);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR);
                console.log(textStatus);
                console.log(errorThrown);
            }

        });
    });
           
    // bind click event to the "Public" in the right side of the page
    $("#public_posts").click(function(e){
        e.preventDefault();
        $.ajax({
              url: "http://"+window.location.host+"/posts/",
              type: "GET",
              success: function(data) {
                  displayJsonData(data["posts"]);
              },
              error: function(jqXHR, textStatus, errorThrown) {
                  console.log(jqXHR);
                  console.log(textStatus);
                  console.log(errorThrown);
              }
              
          });
    });
        
    // bind click event to the "Me" in the right side of the page
    $("#my_posts").click(function(e){
        e.preventDefault();
        var currentUserId = $("h1.blog-title").first().attr("id");
        $.ajax({
              url: "http://"+window.location.host+"/author/"+currentUserId+"/posts/",
              type: "GET",
              success: function(data) {
                  displayJsonData(data["posts"]);
              },
              error: function(jqXHR, textStatus, errorThrown) {
                  console.log(jqXHR);
                  console.log(textStatus);
                  console.log(errorThrown);
              }
              
        });
    });

    // bind click event to anchor element for each friends
    $(".friend_lists").click(function(e){
        e.preventDefault();
        var userid = $(this).attr("id");
        $.ajax({
              url: "http://"+window.location.host+"/author/"+userid+"/posts/",
              type: "GET",
              success: function(data) {
                  displayJsonData(data["posts"]);
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
 * This method is used to get the UUID appended
 * to the HTML ID attribute.
 *
 * @param htmlid    HTML ID attribute containing UUID as part of its ID
 *
 * @return          UUID of the post
 */
function getUuid(htmlid)
{
    var idInfo = htmlid.split("-");
    var uuid = idInfo[1];
    
    for(var i=2; i < idInfo.length; i++)
    {
        uuid += "-"+idInfo[i];
    }
    
    return uuid
}

/**
 *  This method is to bind the click event to the
 *  edit and delete button associated with each posts
 *  made by the currently authenticated user.
 */
function postButtonClickEvent()
{
    $(".post_buttons").click(function(e) {
         e.preventDefault();
         // reactivate the tinymce with the contents inside
         var currentdbId = getUuid($(this).attr("id"));
         
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
}

/**
 * Takes the JSON data returned from the GET requests and
 * displays them in the post wall main page.
 *
 * @param json          JSON data from the AJAX calls
 */
function displayJsonData(json)
{
    var posts = json;
    $(".blog-main").remove();
    var currentUser = $("h1.blog-title").first().text().trim();
    
    for(var i=0; i < posts.length; i++)
    {
        var id = posts[i]["guid"];
        
        var postMainDiv = makePostDiv(id, currentUser, posts[i]);
        
        $("#post_wall_container").append(postMainDiv);
    }
    postButtonClickEvent();
}

/**
 * This method is used to create the HTML to display each of the posts.
 * it takes the information given in the post in a JSON object format
 * and generates the HTML to be displayed.
 *
 * @param   postid      UUID of the post
 * @param   currentUser currently authenticated user
 * @param   post        JSON object containing all information associated with the post
 *
 * @return  jQuery object that represents the top container div for the posts
 */
function makePostDiv(postid, currentUser, post)
{
    var postmain = $("<div id='post_wall-"+postid+"' class='col-sm-8 blog-main'></div>");
    var postdiv = $("<div id='post-"+postid+"' class='blog-post'></div>");
    
    
    // do not display the delete and edit button if the current user is not the author of the post.
    if(currentUser == post["author"].displayname)
    {
        var deleteButton = $('<button id="post_delete-'+postid+'" type="button" class="btn btn-primary btn-lg post_buttons"><span class="glyphicon glyphicon-trash"></span> Delete</button>');
        var editButton = $('<button id="post_edit-'+postid+'" type="button" class="btn btn-primary btn-lg post_buttons"><span class="glyphicon glyphicon-pencil"></span> Edit</button>');
    }
    
    
    var header = $('<h2 class="blog-post-title">'+ post["title"] +'</h2>');
    
    var categories = post["categories"];
    for(var cat_ind = 1; cat_ind < post["categories"].length; cat_ind++)
    {
        categories += ","+ post["categories"][cat_ind];
    }
    var cat_div = $('<div id="post_category-'+postid+'"><p class="blog-post-meta">Categories: <span>'+categories+'</span></p></div>');
    var source = $('<div id="post_source-'+postid+'"><p class="blog-post-meta" style="margin-bottom:2px;">Source: <span>'+post["source"]+'<span></p></div>');
    var origin = $('<div id="post_origin-'+postid+'"><p class="blog-post-meta">Origin: <span>'+post["origin"]+'<span></p></div>');
    var description = $('<div id="post_description-'+postid+'"><p class="blog-post-meta">Description of the Post: <span>'+post["description"]+'</span></p></div>');
    var content = $('<div id="post_content-'+postid+'" class="blog_content">'+post["content"]+'</div>');
    var authorinfo = $('<div id="post_author_info-'+postid+'"><p class="blog-post-meta">Posted on '+post["pubDate"]+' by <a href="#">'+post["author"].displayname+'</a></p></div>');
    var hiddenPermission = $('<input id="post_permission-'+postid+'" type="hidden" value="'+post["visibility"]+'"/>');
    var commentContainer = $('<div id="post_comment-'+postid+'" class="well"></div>');
    var commentHeader = $('<h4> Comments </h4>');
    
    $(commentContainer).append(commentHeader);
    for(var comment_ind = 0; comment_ind < post["comments"].length; comment_ind++)
    {
        
        var comment = post["comments"][comment_ind];
        var commentDiv = $('<div id="post_comment-'+comment.guid+'" class="post_comments"><p> '+comment.comment+' </p><p class="blog-post-meta">Commented by: '+comment.author.displayname+'</p></div>');
        $(commentContainer).append(commentDiv);
    }
    
    var commentForm = $('<div id="post_commentform-'+postid+'" class="well">'+
                        '<div class="form-group">'+
                        '<form class="form-horizontal" action="http://'+window.location.host+'/author/'+currentUser+'/posts/'+postid+'/comments/" method="post">'+
                        '<label for="id_comment" class="col-sm-3">Your comment:</label>'+
                        '<textarea cols="40" id="id_comment" name="comment" rows="10"></textarea>'+
                        '<input type="submit" name="comment_submit_form" class="btn btn-primary" value="Submit" /></form></div></div>');
    
    if(currentUser == post["author"].displayname)
    {
        $(postdiv).append(deleteButton);
        $(postdiv).append(editButton);
    }
    
    $(postdiv).append(header);
    $(postdiv).append(cat_div);
    $(postdiv).append(source);
    $(postdiv).append(origin);
    $(postdiv).append(description);
    $(postdiv).append(content);
    $(postdiv).append(authorinfo);
    $(postdiv).append(hiddenPermission);
    $(postdiv).append(commentContainer);
    $(postdiv).append(commentForm);
    
    $(postmain).append(postdiv);
    return postmain
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
               $.ajax({
                  url: "http://"+window.location.host+"/posts/"+dbId+"/",
                  type: "DELETE",
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
    var bodyContent = $("#post_content-"+currentdbId).html();
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
    submitUpdate();
}

/**
 * This method is used to use AJAX to update the posts
 * that were created by the current user.  It calls
 * http://localhost:8000/posts/<postID>/ webservice with
 * POST method to modify the post.
 */
function submitUpdate()
{
    $("#update_form").submit(function(e) {
         e.preventDefault();
         var currentUser = $("h1.blog-title").first().text().trim();
         var url = $(this).attr("action");
         var guid = getUuid($(this).find("select").first().attr("id"));
         var permissionVal = $("#post_permission-"+guid).val();
         var categoryVal = $("#edit_post_category-"+guid).val();
         var titleVal = $("#post_title-"+guid).val();
         var descriptionVal = $("#edit_post_description-"+guid).val();
         var contentVal = $("#edit_post_content-"+guid).val();
         $.ajax({
                url: url,
                type: "POST",
                data: {
                    "id": guid,
                    "permission": permissionVal,
                    "category": categoryVal,
                    "title": titleVal,
                    "description": descriptionVal,
                    "content": contentVal
                },
                success: function(data) {
                    var newpostDiv = makePostDiv(guid, currentUser, data["posts"][0]);
                
                    $("#edit_post-"+guid).empty().remove();
                    $("#post_wall-"+guid).replaceWith(newpostDiv);
                    postButtonClickEvent();
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    console.log(jqXHR);
                    console.log(textStatus);
                    console.log(errorThrown);
                }
                
          });
     });
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
                    '<form id="update_form" class="form-horizontal" action="http://127.0.0.1:8000/posts/'+id+'/" method="POST">'+
                        '<div class="form-group">'+
                            '<label for="post_permissions" class="col-sm-3">Permissions:</label>'+
                            '<div class="col-sm-9">'+
                                '<select id="edit_post_permissions-'+id+'" name="post_permissions-'+id+'" class="col-sm-9 form-control" style="width: 90%;">'+
                                    '<option value="PUBLIC" selected="selected">Public</option>'+
                                        '<option value="FOAF">Friend of All Friends</option>'+
                                        '<option value="FRIENDS">Friends</option>'+
                                        '<option value="PRIVATE">Private</option>'+
                                        '<option value="SERVERONLY">Server only</option>'+
                                    '</select>'+
                                '</div>'+
                            '</div>'+
                            '<div class="form-group">'+
                                '<label for="post_title-'+id+'" class="col-sm-3">Title: </label>'+
                                '<div class="col-sm-9">'+
                                    '<input type="text" id="post_title-'+id+'" name="post_title-'+id+'" style="width: 90%;" placeholder="Title of the post"/>'+
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