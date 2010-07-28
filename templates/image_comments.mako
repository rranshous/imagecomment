## todo: not have to reload the map + such each time i render the template

<%def name="get_image_comment_list(id)">
<%
    from utils import get_map, config, get_image_comments
    media_map = get_map()
    comments = get_image_comments(media_map[id])
%>
<ul>
% for comment in comments:
    <li>${comment}</li>
% endfor
</ul>
</%def>

${get_image_comment_list(id)}

