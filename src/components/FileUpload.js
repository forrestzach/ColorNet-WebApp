import React from 'react';
import colorNetLogo from '../colorNetLogo.jpg'
import 'bootstrap/dist/css/bootstrap.min.css';
import { Card, Row, Col, Container } from "react-bootstrap";
import CardGroup from 'react-bootstrap';

import Carousel from 'react-bootstrap/Carousel';
import Button from 'react-bootstrap/Button';
import '../App.css';

class Main extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      imageURL: '',
      imageName: '',
      correctedImageName: '',
      test_imageURL: '/root/file-upload/uploads/test_docs/thumb1.jpg',
      correctedImage: null,
      correctedImageURL: '',
      // file: null,
      file: colorNetLogo,
      // file: = {process.env.PUBLIC_URL + '/orange.png'},
      correctedFile:null,
      //following line is correct initial setup, going to try and have placeholder image here too
      // correctedImageBinary: null
      //following line is jsut testing
      // uploadInput: [],
      files: null,
      correctImageNamesArray: [],
      correctImagesList: [],
      //very perplexed by how I should go about ensuring that the names and images are in line
      // i probably need to make a list of dicts so that everything stays together nicely.
      correctImageBinaryArray: [],
      index : 0,
      // setIndex : 0,

      // handleSelect : (selectedIndex, e) => {
      //   setIndex(selectedIndex);
      // }
    };

    this.handleUploadImage = this.handleUploadImage.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.handleUpdateImage = this.handleUpdateImage.bind(this);
    this.handleUpdateImage2 = this.handleUpdateImage2.bind(this);
    this.handleUpdateImage3 = this.handleUpdateImage3.bind(this);
    this.imageErrorFunction = this.imageErrorFunction(this);
    this.handleUploadImageMultiple = this.handleUploadImageMultiple.bind(this);
    this.handleUploadImageMultiSingle = this.handleUploadImageMultiSingle.bind(this);
    this.handleDownloadFiles = this.handleDownloadFiles.bind(this);

    this.handleSelect = this.handleSelect.bind(this);
    this.handleFindIndex = this.handleFindIndex.bind(this);


  }

  handleSelect(selectedIndex, e) {
    this.setState({
      index: selectedIndex,
    });
  }
  

  imageErrorFunction(event){
    console.log("error again")
  }

  //This is for displaying the initial image
  handleChange(event){
    console.log(event.target.files[0])
    this.setState({
      file: URL.createObjectURL(event.target.files[0])
  
    })
  }

  handleFindIndex(fileName){
    for(let i = 0; i < ((this.state.correctImageNamesArray).length); i++){
      if(this.state.correctImageNamesArray[i] == fileName){
        return i;
      }
    }
  }
  //i am pretty sure this is updating the image as it fails the get request after the fact 
  //This does not really work well, inexplicably fails pretty often.
  handleUpdateImage(fileName){
    console.log(fileName)
    setTimeout(() =>  { this.setState({
      correctedImageURL: `${process.env.PUBLIC_URL}/corrected_images/${fileName}`
      // correctedFile: URL.createObjectURL((this.correctedImageURL).blob())
    })  
      //this.state.correctedFile = URL.createObjectURL((this.correctedImageURL).blob())
      // fetch(this.state.correctedImageURL)
      // .then(res => res.blob())
      // .then(blob => {
      //   this.state.correctedFile = URL.createObjectURL(blob);
        
      // })
    }, 3000);
    console.log(`${process.env.PUBLIC_URL}/corrected_images/${fileName}`)
  }

  handleUpdateImage2(fileName){
    console.log("updateImage2 called");
    //I know that this is not at all proper, this is more just testing the endpoint it it cna receive the calls correctly.
    //this.correctedImageURL = fetch('/api/getImage?image=' + fileName, {method: 'GET'});
    fetch('/api/getImage?image=' + fileName, {method: 'GET'}).then((response) => {
      response.json().then((body) => {
        console.log("inside fetch");
        console.log(body.msg)
        // this.state.correctedImageBinary = body.img
        this.setState({correctedImageBinary: body.img})
      });
    });
  }

  handleUpdateImage3(fileName){
    console.log("updateImage3 called");
    //I know that this is not at all proper, this is more just testing the endpoint it it cna receive the calls correctly.
    //this.correctedImageURL = fetch('/api/getImage?image=' + fileName, {method: 'GET'});
    fetch('/api/getImage?image=' + fileName, {method: 'GET'}).then((response) => {
      response.json().then((body) => {
        var currentIndex = -1;
        for(let i = 0; i < ((this.state.correctImageNamesArray).length); i++){
          if(this.state.correctImageNamesArray[i] == fileName){
            currentIndex = i;
          }
        }

        // this.setState({correctedImageBinary: body.img})
        // this.setState({correctImageBinaryArray[currentIndex]: body.img})
        // console.log("binary  update: " + body.img);
        this.state.correctImageBinaryArray[currentIndex] = body.img;
      });
    });
  }

  // working post method
  handleUploadImage(ev) {
    ev.preventDefault();
    console.log("hey")
    const data = new FormData();
    data.append('file', this.uploadInput.files[0]);
    fetch('/api/upload', {
      method: 'POST',
      body: data,
      'Content-Type': 'image/*',
    }).then((response) => {
      response.json().then((body) => {
        // this.setState({ imageURL: `../../../uploads/test_docs/${body.file}` });
        console.log(body)
        this.setState({correctedImageName: `${body.CorrectedFileName}`})
        //this.setState({correctedImage: })
        console.log("new correctedImageName: ")
        // this is the one which i have been using //this.handleUpdateImage(body.CorrectedFileName)
        //Subsequent line is new attempt
        this.handleUpdateImage2(body.CorrectedFileName)
      });
    });
    console.log("finish")
  }

  handleUploadImageMultiSingle(){
    console.log("multi single func");
    console.log((this.uploadInput.files).length);
    this.setState({correctImageNamesArray: []});

    //TODO gotta make a few more changes to ensure it is using the array of filenames/image data
    for(let i = 0; i < ((this.uploadInput.files).length); i++){
      const data = new FormData();
      data.append('file', this.uploadInput.files[i]);
      fetch('/api/upload', {
        method: 'POST',
        body: data,
      }).then((response) => {
        response.json().then((body) => {
          console.log(body);
          this.setState({correctImageBinaryArray: [...this.state.correctImageBinaryArray, 'placeholder']})
          this.setState({correctImageNamesArray: [...this.state.correctImageNamesArray, `${body.CorrectedFileName}`]})
          this.handleUpdateImage3(body.CorrectedFileName)
        });
      });
    }
    console.log(this.state.correctImageNamesArray);
    console.log("binaryArray _"+ this.state.correctImageBinaryArray + "_")
  }

  handleDownloadFiles(){
    console.log("inside download function");
    console.log(this.state.correctImageNamesArray);
    for(let i = 0; i < ((this.state.correctImageNamesArray).length); i++){
      fetch('/api/downloadImage?image=' + this.state.correctImageNamesArray[i], {method: 'GET'})
      .then(response => response.blob())
      .then(blob => {
          var url = window.URL.createObjectURL(blob);
          var a = document.createElement('a');
          a.href = url;
          // a.download = "filename.xlsx";
          a.download = this.state.correctImageNamesArray[i]
          document.body.appendChild(a); // we need to append the element to the dom -> otherwise it will not work in firefox
          a.click();    
          a.remove();
      });
    }
  }

  handleUploadImageMultiple() {
    console.log("in multiple");
    const data = new FormData();
    console.log((this.uploadInput.files).length);
    data.append('numImages', (this.uploadInput.files).length);
    for(let i = 0; i< (this.uploadInput.files).length; i++){
      console.log(this.uploadInput.files[i]);
      // data.append('file', this.uploadInput.files[i]);
      // data.append('filename', this.fileName.value);
      this.currentImageKey = "image" + i;
      // console.log(this.currentImageKey);
      data.append(this.currentImageKey, this.uploadInput.files[i]);

    }
    // console.log(data);
    fetch('/api/uploadMultiple', {
      method: 'POST',
      body: data,
    }).then((response) => {
      response.json().then((body) => {
        console.log(body);
      });
    });
  }


  render() {
    return (
      <div>
        <div className="inputButton">
          <input variant="primary" ref={(ref) => { this.uploadInput = ref; }} type="file"  onChange={this.handleChange} multiple />
          {/* <input type="file" onChange={this.handleChange} /> */}
        </div>
        <br />
        {/* Multiple image upload, does work now*/}
        {/* <div>
          <button type="button" onClick={() => {this.handleUploadImageMultiple()}}>Process Multiple</button>
        </div> */}
        {/* Following is working implementation for single images */}
        {/* <div>
          <button type="button" onClick={this.handleUploadImage}>Process</button>
        </div> */}
        {/*Multi Single image upload*/}
        <div className="centerButton">
          <button variant="secondary" type="button" onClick={this.handleUploadImageMultiSingle}>Process Multiple</button>
        </div>

        {/* FOLLOWING LINE IS PROPER FUNCITONALITY */}
        {/* <img src = {this.state.file} alt = "original"/> */}
        <p> {this.state.correctedImageName} </p>
        {/* <img src = {`${process.env.PUBLIC_URL}/corrected_images/${this.state.correctedImageURL}`} alt = "corrected image" /> */}
        
        {/* TODO FOLLOWING LINE IS WHAT USED TO WORK BEFORE GET FUNC */}
        {/* <img src = {this.state.correctedImageURL} alt = "corrected"/> */}
        {/* <img src = {this.state.correctedFile} alt = "Corrected Image"/> */}

        {/* CORR FOLLOWING LINE IS NEW PROPER FUNCTIONALITY */}
        {/* {this.state.correctedImageBinary ? <img src={`data:image/jpg;base64,${this.state.correctedImageBinary}`}/>: ''} */}
        
        <br/>

        {/* <div className="CompareImage">
        {/* <div style={{maxWidth: '600px'}}> */}
        {/*  <ReactCompareImage leftImage = {this.state.file} rightImage = {`data:image/jpg;base64,${this.state.correctedImageBinary}`} />
        </div> */}

        {/* <Container>
          <Row>
            {this.state.correctImageNamesArray.map((k) => (
              <Col key={k} xs={12} md={4} lg={3}>
                <Card>
                  <Card.Img src="https://via.placeholder.com/150x75"/>

                  <Card.Body>
                    <Card.Title> {this.state.correctImageNamesArray[k]} </Card.Title>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        </Container> */}
        {/* <Container  style={{maxWidth: '100%', height: 'auto'}}> */}
        <Container className="CaroContainer"> 
          {/* <Carousel variant="dark" activeIndex={this.state.index} onSelect={this.state.handleSelect}> */}
          {/* <Carousel variant="dark" onSelect={this.handleSelect()}> */}
          <Carousel className="CaroCarousel" variant="dark" slide={false} touch={true} interval={null} activeIndex={this.state.index} onSelect={this.handleSelect}>
            {/*working implementation, just want to test and play around {this.state.correctImageNamesArray.map((k) => ( */}
            {this.state.correctImageNamesArray.map(() => (
              <Carousel.Item className="CaroItem">
                {/* <img src="https://via.placeholder.com/150x75"/> */}
                <div >
                  <img className="CaroImage" src={`data:image/jpg;base64,${this.state.correctImageBinaryArray[this.state.index]}`}/>
                  {/* <ReactCompareImage leftImage = {this.uploadInput.files[this.state.index]} rightImage = {`data:image/jpg;base64,${this.state.correctImageBinaryArray[this.state.index]}`} /> */}
                </div>
                <Carousel.Caption>
                  {/* Deliberately removed<p>{this.state.correctImageNamesArray[this.state.index]}</p> */}
                  {console.log("index " + this.state.index)}
                </Carousel.Caption>
              </Carousel.Item>
            ))}
          </Carousel>
        </Container>

        <br/>
        {/* <CardGroup>
          {this.state.correctImageNamesArray.map(() => (
              <Card>
                <Card.Img src
              </Card>
          ))}
        </CardGroup> */}
        <Container>
          <Row>
            {this.state.correctImageNamesArray.map((k) => (
              <Col key={k} xs={12} md={4} lg={3}>
                <Card onChange={console.log(k + " Clicked!")}>
                  {/* {cardDataIndex = this.handleFindIndex(k)} */}
                  <Card.Img src={`data:image/jpg;base64,${this.state.correctImageBinaryArray[this.handleFindIndex(k)]}`}/>
                  {console.log("k: " + k + " cardDataIndex: " + this.handleFindIndex(k))}

                  <Card.Body>
                    <Card.Title> {this.state.correctImageNamesArray[this.handleFindIndex(k)]} </Card.Title>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        </Container>

        {/* <div>
          <button type="button" >Share</button>
        </div> */}
        <br/>
        <div className="centerButton">
          <button type="button" onClick={this.handleDownloadFiles}>Download Images</button>
        </div>
      </div>
    );
  }
}

export default Main;