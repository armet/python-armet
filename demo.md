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

### User creates a poll

```
POST /poll
```

### User adds a choice to a poll

```
POST /poll/{id}/choice
```

### User removes a choice from a poll

```
DELETE /poll/{id}/choice/{id}
```

### User publishes a poll (?)

```
POST /poll/{id}/publish
```

### User votes for a choice on a poll

```
POST /poll/{id}/choice/{id}/vote
```
