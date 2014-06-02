# Database Tables

These are the database tables which comprise the myweb database. They're all 
meant to be as normalized as possible, to avoid redundancy.

## ARTICLES

    +-------------+-----------------+----------------+
    | Url: String | Article: BINARY | Domain: String |
    +-------------+-----------------+----------------+

 - The Url column contains the Url of the page that the article is about.
 - The Article column contains the level 6 zlib-compressed text of the article.
 - The Domain column contains the domain of the Url given in the Url column.

## LINKS

    +-------------+----------------+
    | Url: String | Linked: String |
    +-------------+----------------+

 - See ARTICLES for the meaning of the Url column.
 - The Linked column is another Url which is linked by the article in the Url column.

## TAGS

    +-------------+-------------+
    | Url: String | Tag: String |
    +-------------+-------------+

 - See ARTICLES for the meaning of the Url column.
 - The Tag column lists a tag given to the article in the Url column.
