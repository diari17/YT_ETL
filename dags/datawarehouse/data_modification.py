import logging

logger = logging.getLogger(__name__)
table = "yt_api"


def insert_rows(cur, conn, schema, row):
    video_id_key = "video_id" if schema == "staging" else "Video_ID"
    try:
        if schema == "staging":
            cur.execute(
                f"""
                INSERT INTO {schema}.{table}
                    ("Video_ID", "Video_Title", "Upload_Date", "Duration",
                     "Video_Views", "Likes_Count", "Comments_Count")
                VALUES
                    (%(video_id)s, %(title)s, %(publishedAt)s, %(duration)s,
                     %(viewCount)s, %(likeCount)s, %(commentCount)s);
                """,
                row,
            )
        else:
            cur.execute(
                f"""
                INSERT INTO {schema}.{table}
                    ("Video_ID", "Video_Title", "Upload_Date", "Duration",
                     "Video_Views", "Likes_Count", "Comments_Count")
                VALUES
                    (%(Video_ID)s, %(Video_Title)s, %(Upload_Date)s, %(Duration)s,
                     %(Video_Views)s, %(Likes_Count)s, %(Comments_Count)s);
                """,
                row,
            )

        conn.commit()
        logger.info(f"Ligne insérée avec Video_ID: {row[video_id_key]}")

    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur lors de l'insertion : {row.get(video_id_key)} - {e}")
        raise


def update_rows(cur, conn, schema, row):
    if schema == "staging":
        video_id = "video_id"
        upload_date = "publishedAt"
        video_title = "title"
        video_views = "viewCount"
        likes_count = "likeCount"
        comments_count = "commentCount"
    else:
        video_id = "Video_ID"
        upload_date = "Upload_Date"
        video_title = "Video_Title"
        video_views = "Video_Views"
        likes_count = "Likes_Count"
        comments_count = "Comments_Count"

    try:
        cur.execute(
            f"""
            UPDATE {schema}.{table}
            SET
                "Video_Title" = %({video_title})s,
                "Video_Views" = %({video_views})s,
                "Likes_Count" = %({likes_count})s,
                "Comments_Count" = %({comments_count})s
            WHERE "Video_ID" = %({video_id})s
              AND "Upload_Date" = %({upload_date})s;
            """,
            row,
        )

        conn.commit()
        logger.info(f"Ligne mise à jour avec Video_ID: {row[video_id]}")

    except Exception as e:
        conn.rollback()
        logger.error(f"Erreur lors de la mise à jour : {row.get(video_id)} - {e}")
        raise


def delete_rows(cur, conn, schema, ids_to_delete):
    ids_to_delete = list(ids_to_delete)
    try:
        cur.execute(
            f"""
            DELETE FROM {schema}.{table}
            WHERE "Video_ID" = ANY(%s);
            """,
            (ids_to_delete,),
        )

        conn.commit()
        logger.info(f"Video_IDs des ligne(s) supprimée(s) : {ids_to_delete}")

    except Exception as e:
        conn.rollback()
        logger.error(
            f"Erreur lors de la suppression des vidéos avec comme Video_ID : {ids_to_delete} - {e}"
        )
        raise