import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import axios from 'axios';
import '../css/main.css';

class Player extends Component {
    constructor(props) {
        super(props);
        this._renderImg = this._renderImg.bind(this);
    }

    _onError(e) {
        e.target.src='https://vignette.wikia.nocookie.net/webarebears/images/6/69/Panda_Standing.png/revision/latest/scale-to-width-down/180?cb=20150728014556'
    }

    _renderImg() {
        let images = [];
        for (var i in this.props.images) {
            let link = this.props.images[i];
            images.push(<img onError={this._onError} src={link} class='img'/>);
        }
       console.log(images);
        return(images);
    }

    render() {
        return (
            <div>
                    <div class='row'>
                        <div class='header'>
                            <h4>{this.props.name}</h4>
                        </div>
                        <div class='body'>
                            {this._renderImg()}
                        </div>
                    </div>
            </div>
        );
    }
}

class OWS extends Component {
    constructor() {
        super();
        this.state = {
            list: [],
            hello: <div>helloworld</div>,
        };
        this.getPlayers = this.getPlayers.bind(this);
        this.getPlayers();
    }
    getPlayers() {
        let list = [];
        axios.get('/api/play').then((resp) => {
            const players = resp.data;
            console.log(players);
            for (var player in players) {
                let p = players[player];
                let img_keys = ['char_one_image', 'char_two_image', 'char_three_image', 'char_four_image', 'char_five_image'];
                let imgs = img_keys.map(img => p[img]);
                list.push(<Player name={p['player_tag']} images={imgs} />);
            }
            this.setState({list});
            console.log(this.state.list);
        })
        .catch((err) => {
            console.log(err);
        });
    }
    render() {
        return(
            <div class='wrapper'>
                {this.state.list}
            </div>
        )
    }
}

ReactDOM.render(<OWS />, document.getElementById('container'))
