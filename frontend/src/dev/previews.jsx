import React from 'react'
import {ComponentPreview, Previews} from '@react-buddy/ide-toolbox'
import {PaletteTree} from './palette'
import SignupPage from "../components/SignupPage";

const ComponentPreviews = () => {
    return (
        <Previews palette={<PaletteTree/>}>
            <ComponentPreview path="/SignupPage">
                <SignupPage/>
            </ComponentPreview>
        </Previews>
    )
}

export default ComponentPreviews