odoo.define('social_bit.social_stream_post_kanban_controller', function (require) {
"use strict";

var StreamPostKanbanController = require('social.social_stream_post_kanban_controller');
var StreamPostBitComments = require('social.StreamPostBitComments');

StreamPostKanbanController.include({
    events: _.extend({}, StreamPostKanbanController.prototype.events, {
        'click .o_social_bit_comments': '_onBitCommentsClick',
        'click .o_social_bit_likes': '_onbitPostLike'
    }),

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    _onBitCommentsClick: function (ev) {
        var self = this;
        var $target = $(ev.currentTarget);

        var postId = $target.data('postId');
        this._rpc({
            model: 'social.stream.post',
            method: 'get_bit_comments',
            args: [[postId]]
        }).then(function (result) {
            new StreamPostBitComments(
                self,
                {
                    postId: postId,
                    originalPost: $target.data(),
                    streamId: $target.data('streamId'),
                    accountId: $target.data('bit-account-id'),
                    allComments: result.comments
                }
            ).open();
        });
    },

    _onbitPostLike: function (ev) {
        ev.preventDefault();
        var $target = $(ev.currentTarget);
        var userLikes = $target.data('userLikes');
        // this._rpc({
        //     route: _.str.sprintf('social_twitter/%s/like_tweet', $target.data('streamId')),
        //     params: {
        //         tweet_id: $target.data('twitterTweetId'),
        //         like: !userLikes
        //     }
        // });

        // this._updateLikesCount($target);
        // $target.toggleClass('o_social_twitter_user_likes');
    }
});

return StreamPostKanbanController;

});
