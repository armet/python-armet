# Models

 - Poll
   - question
   - publish_date
   - close_date
   - choice(s) [relationship]

 - Choice
   - poll [relationship]
   - text

 - Vote
   - choice [relationship]
   - date

# Stories
> Using "user" in the general sense (no auth yet)

 - User creates a poll
 - User adds a choice to a poll
 - User removes a choice from a poll
 - User publishes a poll
 - User votes for a choice on a poll
