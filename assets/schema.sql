CREATE TABLE IF NOT EXISTS games (
    game_id text primary key,
    timestamp integer,
    MissionBagBoss_0 integer,
    MissionBagBoss_1 integer,
    MissionBagBoss_2 integer,
    MissionBagBoss_3 integer,
    MissionBagFbeGoldBonus integer,
    MissionBagFbeHunterXpBonus integer,
    MissionBagIsFbeBonusEnabled integer,
    MissionBagIsHunterDead integer,
    MissionBagIsQuickPlay integer,
    MissionBagNumAccolades integer,
    MissionBagNumEntries integer,
    MissionBagNumTeams integer,
    MissionBagTeamDetailsVersion integer,
    HunterLevel integer
);
CREATE TABLE IF NOT EXISTS teams (
    timestamp integer,
    game_id text,
    team_num integer,
    handicap integer,
    isinvite integer,
    mmr integer,
    numplayers integer,
    ownteam integer,
    primary key (
        game_id,
        team_num
)
);
CREATE TABLE IF NOT EXISTS hunters (
    timestamp integer,
    game_id text,
    team_num integer,
    hunter_num integer,
    blood_line_name text,
    bountyextracted integer,
    bountypickedup integer,
    downedbyme integer,
    downedbyteammate integer,
    downedme integer,
    downedteammate integer,
    hadWellspring integer,
    hadbounty integer,
    ispartner integer,
    issoulsurvivor integer,
    killedbyme integer,
    killedbyteammate integer,
    killedme integer,
    killedteammate integer,
    mmr integer,
    profileid integer,
    proximity integer,
    proximitytome integer,
    proximitytoteammate integer,
    skillbased integer,
    teamextraction integer,
    primary key (
        game_id,
        team_num,
        hunter_num
    )
);
CREATE TABLE IF NOT EXISTS entries (
    timestamp integer,
    game_id text,
    entry_num integer,
    amount integer,
    category text,
    descriptorName text,
    descriptorScore integer,
    descriptorType integer,
    iconPath text,
    iconPath2 text,
    reward integer,
    rewardSize integer,
    uiName text,
    uiName2 text,
    primary key (
        game_id,
        entry_num
    )
);