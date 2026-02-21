db.createUser(
    {
        user: "tsn_user",
        pwd: "tsn_password",
        roles: [
            {
                role: "readWrite",
                db: "tsn_bot"
            }
        ]
    }
);
