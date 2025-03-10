import React, { useState } from "react";
import { EditorCardProps } from "./editor-card.props";
import { Card } from "../../card";
import styled from "styled-components";
import { motion } from "framer-motion"


export const EditorCard: React.FC<EditorCardProps> = () => {

    const [isCollapsed, setIsCollapsed] = useState(true)

    const [switchState, setSwitchState] = useState<string>()

    const StyledCard = styled(Card)`
        height: 100%;
    `

    return (
        <motion.div
                layoutId="sidebar"
                initial={{width:50}}
                animate={{width: isCollapsed ? 50:300}}
                transition={{duration:0.3 , ease: "easeInOut"}}
            >
            <StyledCard>
                <button onClick={() => setIsCollapsed(!isCollapsed)}></button>

            </StyledCard>
        </motion.div>

    )
}
