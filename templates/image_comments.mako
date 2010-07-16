<%def name="get_image_comment_list(id)">
<%
    from utils import get_map, config, get_image_comments
    media_map = get_map()
    comments = get_image_comments(media_map[id])
%>
    ${comments}
</%def>

${get_image_comment_list(id)}

