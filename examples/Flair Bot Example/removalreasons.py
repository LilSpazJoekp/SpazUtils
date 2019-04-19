header = """Hi {author}, thanks for submitting to /r/{subreddit.display_name}!

However, your submission has been removed. This action was taken because:"""
footer = "If you disagree with this action, you can [message the mods](https://www.reddit.com/message/compose?to=%2Fr%2F{subreddit.display_name}). Please include a link to your post so that we can see it."


flairList = {
    "removed - repost": {
        "description": "Repost",
        "commentReply": f"{header}\n\nIt's a repost\n\n{footer}"
    },
    "removed - no titles as meme captions": {
        "description": "Title as meme caption",
        "commentReply": f"{header}\n\nWe do not allow titles as meme captions. Feel free to caption it and post again.\n\n{footer}"
    },
    "removed - low effort": {
        "description": "Low effort",
        "commentReply": f"{header}\n\nIt's really low effort content.\n\n{footer}"
    },
    "flairtext": {
        "description": "This the description that gets sent to the log channel",
        "commentReply": "blah blah blah\n\nsupports multiple lines",
        "lock": True,
        "ban": {
            "duration": 1,
            "ban_reason": "Ban reason (str)",
            "ban_message": "Sent to user (str)",
            "ban_note": "Private Mod note (str)"
        },
        "usernote": {
            "usernote": "Note",
            "usernoteWarningType": "spamwatch"
        }
    },
}